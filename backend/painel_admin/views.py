from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from contas.auditoria import RegistroDeAuditoria
from contas.desativacao import DesativacaoNegada, desativar_usuario
from contas.models import TIPOS_INTERNOS, Instituicao, Perfil, TipoInstituicao
from creditos.excecoes import AlocacaoSemConfirmacaoError
from limites.models import AssinaturaInstituicao
from limites.ciclo import ciclo_atual
from limites.normalizacao import cota_da_conta
from limites.servico import calcular_cobranca, estado_cota

from .escopo import escopo_do_painel
from .monitoramento import (
    consumo_por_conta,
    consumo_por_fornecedor,
    contratos_para_o_painel,
)
from .permissoes import (
    exige_acesso_ao_painel,
    exige_staff_interno,
    exige_superadmin,
)
from .forms.conta_teste import ContaTesteForm
from .forms.editar_instituicao import InstituicaoEdicaoForm
from .forms.editar_usuario import UsuarioEdicaoForm
from .forms.instituicao import InstituicaoForm
from .services.alterar_perfil import MotivoObrigatorio, PerfilInvalido, alterar_perfil
from .services.arquivar_instituicao import (
    ACAO_ARQUIVAR,
    ACAO_DESARQUIVAR,
    ACAO_DESATIVAR_CONTA,
    ACAO_REATIVAR_CONTA,
    ArquivamentoInstituicaoNegado,
    arquivar_instituicao,
    desarquivar_instituicao,
)
from .services.criar_conta_teste import ContaTesteJaExisteError, criar_conta_teste
from .services.criar_instituicao import InstituicaoJaExisteError, criar_instituicao
from .services.editar_instituicao import InstituicaoEdicaoNegada, editar_instituicao
from .services.editar_usuario import UsuarioEdicaoNegada, editar_usuario
from .services.zerar_creditos import SaldoJaZeradoError, zerar_creditos_usuario


Usuario = get_user_model()


POR_PAGINA = 25

# O filtro de acoes saia de um `DISTINCT` sobre a tabela de auditoria inteira,
# a cada carga da pagina - a tabela que mais cresce no sistema, sem indice em
# `acao`. O conjunto e finito e conhecido no codigo, entao vem daqui.
ACOES_AUDITADAS = (
    "alterar_perfil",
    "alterar_plano_instituicao",
    ACAO_ARQUIVAR,
    "criar_conta_teste",
    "criar_instituicao",
    ACAO_DESARQUIVAR,
    ACAO_DESATIVAR_CONTA,
    "desativar_usuario",
    "editar_instituicao",
    "editar_usuario",
    ACAO_REATIVAR_CONTA,
    "aprovar_nota",
    "alterar_nota",
    "oficializar_prova",
    "zerar_creditos",
)


def superadmin_required(view):
    """Acesso irrestrito: financeiro, entidade de dominio e auditoria."""
    return login_required(exige_superadmin(view))


def staff_interno_required(view):
    """Gestao de usuario e monitoramento cross-tenant: provider ou administrador."""
    return login_required(exige_staff_interno(view))


def painel_required(view):
    """Leitura no painel, recortada pela hierarquia da conta logada.

    Admite tambem o DIRETOR - que enxerga somente a propria escola, pelo
    recorte de `escopo.py`. Toda view com este decorator PRECISA consultar o
    escopo em vez de ler o modelo direto.
    """
    return login_required(exige_acesso_ao_painel(view))


def _paginar(request, queryset):
    return Paginator(queryset, POR_PAGINA).get_page(request.GET.get("pagina"))


@painel_required
def dashboard(request):
    escopo = escopo_do_painel(request.user)
    # A auditoria e global por natureza (registra acao de plataforma), entao so
    # a equipe interna a le. O diretor ve o recorte da propria escola.
    if escopo.cross_tenant:
        recentes = RegistroDeAuditoria.objects.select_related("ator").order_by("-criado_em")[:12]
        auditorias = RegistroDeAuditoria.objects.count()
    else:
        recentes = []
        auditorias = None
    contexto = {
        "escopo": escopo,
        "usuarios": escopo.usuarios().count(),
        "instituicoes": escopo.instituicoes().count(),
        "auditorias": auditorias,
        "recentes": recentes,
    }
    return render(request, "painel_admin/dashboard.html", contexto)


@staff_interno_required
def instituicoes(request):
    formulario = InstituicaoForm(request.POST or None)
    if request.method == "POST" and formulario.is_valid():
        try:
            instituicao = criar_instituicao(ator=request.user, **formulario.cleaned_data)
        except (InstituicaoJaExisteError, ValueError) as erro:
            formulario.add_error("documento", str(erro))
        else:
            messages.success(request, f"Instituicao {instituicao.nome} criada com sucesso.")
            return redirect("painel-instituicoes")

    # Paginado, nao cortado em 100: o corte silencioso fazia a 101a escola
    # simplesmente nao existir para o superadmin, sem aviso nenhum na tela.
    contexto = {
        "formulario": formulario,
        "pagina": _paginar(request, Instituicao.objects.order_by("nome")),
    }
    return render(request, "painel_admin/instituicoes.html", contexto)


@painel_required
def instituicao(request, pk):
    escopo = escopo_do_painel(request.user)
    alvo = get_object_or_404(escopo.instituicoes(), pk=pk)
    formulario = InstituicaoEdicaoForm(
        initial={"nome": alvo.nome, "documento": alvo.documento or ""}
    )
    try:
        cobranca = calcular_cobranca(alvo)
    except AssinaturaInstituicao.DoesNotExist:
        cobranca = None
    return render(
        request,
        "painel_admin/instituicao.html",
        {"escopo": escopo, "alvo": alvo, "formulario": formulario, "cobranca": cobranca},
    )


@superadmin_required
@require_POST
def instituicao_editar(request, pk):
    alvo = get_object_or_404(Instituicao, pk=pk)
    if alvo.tipo in TIPOS_INTERNOS:
        return HttpResponseBadRequest("Instituição interna da equipe não é editada por este fluxo.")
    formulario = InstituicaoEdicaoForm(request.POST)
    if not formulario.is_valid():
        return render(request, "painel_admin/instituicao.html", {"alvo": alvo, "formulario": formulario})
    try:
        editar_instituicao(ator=request.user, alvo=alvo, motivo=request.POST.get("motivo", ""), **formulario.cleaned_data)
    except InstituicaoEdicaoNegada as erro:
        formulario.add_error(None, str(erro))
        return render(request, "painel_admin/instituicao.html", {"alvo": alvo, "formulario": formulario})
    messages.success(request, f"Instituição {alvo.nome} atualizada.")
    return redirect("painel-instituicao", pk=alvo.pk)


@superadmin_required
@require_POST
def instituicao_arquivar(request, pk):
    alvo = get_object_or_404(Instituicao, pk=pk)
    try:
        arquivar_instituicao(
            ator=request.user,
            alvo=alvo,
            confirmado=request.POST.get("confirmacao") == "on",
            motivo=request.POST.get("motivo", ""),
        )
    except ArquivamentoInstituicaoNegado as erro:
        return HttpResponseBadRequest(str(erro))
    messages.success(request, f"Instituição {alvo.nome} arquivada. Os dados foram preservados.")
    return redirect("painel-instituicoes")


@superadmin_required
@require_POST
def instituicao_desarquivar(request, pk):
    alvo = get_object_or_404(Instituicao, pk=pk)
    try:
        desarquivar_instituicao(
            ator=request.user,
            alvo=alvo,
            confirmado=request.POST.get("confirmacao") == "on",
            motivo=request.POST.get("motivo", ""),
        )
    except ArquivamentoInstituicaoNegado as erro:
        return HttpResponseBadRequest(str(erro))
    messages.success(
        request,
        f"Instituição {alvo.nome} reaberta. Voltaram apenas as contas que o arquivamento desativou.",
    )
    return redirect("painel-instituicao", pk=alvo.pk)


@superadmin_required
def contas_teste(request):
    formulario = ContaTesteForm(request.POST or None)
    if request.method == "POST" and formulario.is_valid():
        dados = formulario.cleaned_data.copy()
        senha = dados.pop("password1")
        dados.pop("password2")
        dados["nome"] = dados.pop("first_name")
        dados["sobrenome"] = dados.pop("last_name")
        try:
            conta = criar_conta_teste(ator=request.user, senha=senha, **dados)
        except (ContaTesteJaExisteError, ValueError) as erro:
            formulario.add_error("email", str(erro))
        else:
            messages.success(
                request,
                f"Conta de teste criada: {conta.email}. A senha nao sera exibida novamente.",
            )
            return redirect("painel-contas-teste")

    contexto = {"formulario": formulario}
    return render(request, "painel_admin/contas_teste.html", contexto)


@painel_required
def usuarios(request):
    escopo = escopo_do_painel(request.user)
    consulta = request.GET.get("q", "").strip()
    perfil = request.GET.get("perfil", "").strip()
    queryset = escopo.usuarios().order_by("email")
    if consulta:
        queryset = queryset.filter(Q(email__icontains=consulta) | Q(first_name__icontains=consulta))
    if perfil in Perfil.values:
        queryset = queryset.filter(perfil=perfil)
    contexto = {
        "escopo": escopo,
        "pagina": _paginar(request, queryset),
        "consulta": consulta,
        "perfil": perfil,
        "perfis": Perfil.choices,
    }
    return render(request, "painel_admin/usuarios.html", contexto)


@painel_required
def usuario(request, pk):
    escopo = escopo_do_painel(request.user)
    # `get_object_or_404` sobre a queryset do escopo, e nao sobre `Usuario`:
    # conta de outra escola precisa ser indistinguivel de conta inexistente.
    alvo = get_object_or_404(escopo.usuarios(), pk=pk)
    formulario_edicao = UsuarioEdicaoForm(
        alvo=alvo,
        initial={
            "email": alvo.email,
            "first_name": alvo.first_name,
            "last_name": alvo.last_name,
            "instituicao": alvo.instituicao_id,
            "perfil": alvo.perfil,
            "ativo": alvo.ativo,
        },
    )
    contexto = {
        "escopo": escopo,
        "alvo": alvo,
        "perfis": Perfil.choices,
        "cota": cota_da_conta(estado_cota(alvo)),
        "formulario_edicao": formulario_edicao,
    }
    return render(request, "painel_admin/usuario.html", contexto)


@staff_interno_required
@require_POST
def usuario_editar(request, pk):
    alvo = get_object_or_404(Usuario.objects.select_related("instituicao"), pk=pk)
    formulario = UsuarioEdicaoForm(alvo=alvo, data=request.POST)
    if not formulario.is_valid():
        contexto = {
            "alvo": alvo,
            "perfis": Perfil.choices,
            "cota": estado_cota(alvo),
            "formulario_edicao": formulario,
        }
        return render(request, "painel_admin/usuario.html", contexto)
    try:
        dados = formulario.cleaned_data.copy()
        dados["nome"] = dados.pop("first_name")
        dados["sobrenome"] = dados.pop("last_name")
        editar_usuario(
            ator=request.user,
            alvo=alvo,
            motivo=request.POST.get("motivo", ""),
            **dados,
        )
    except UsuarioEdicaoNegada as erro:
        formulario.add_error(None, str(erro))
        contexto = {
            "alvo": alvo,
            "perfis": Perfil.choices,
            "cota": estado_cota(alvo),
            "formulario_edicao": formulario,
        }
        return render(request, "painel_admin/usuario.html", contexto)
    messages.success(request, f"Conta {alvo.email} atualizada.")
    return redirect("painel-usuario", pk=alvo.pk)


@superadmin_required
def registros(request):
    acao = request.GET.get("acao", "").strip()
    consulta = request.GET.get("q", "").strip()
    queryset = RegistroDeAuditoria.objects.select_related("ator").order_by("-criado_em")
    if acao:
        queryset = queryset.filter(acao=acao)
    if consulta:
        queryset = queryset.filter(
            Q(ator__email__icontains=consulta) | Q(objeto_id__icontains=consulta) | Q(motivo__icontains=consulta)
        )
    contexto = {
        "pagina": _paginar(request, queryset),
        "acao": acao,
        "consulta": consulta,
        "acoes": ACOES_AUDITADAS,
    }
    return render(request, "painel_admin/registros.html", contexto)


@superadmin_required
@require_POST
def usuario_perfil(request, pk):
    alvo = get_object_or_404(Usuario, pk=pk)
    try:
        alterar_perfil(
            alvo=alvo,
            ator=request.user,
            perfil=request.POST.get("perfil", ""),
            motivo=request.POST.get("motivo", ""),
        )
    except (MotivoObrigatorio, PerfilInvalido) as erro:
        return HttpResponseBadRequest(str(erro))
    return redirect("painel-usuario", pk=alvo.pk)


@painel_required
@require_POST
def usuario_desativar(request, pk):
    # Pelo escopo, e nao por `Usuario`: buscar global fazia a conta de outra
    # escola responder 400 ("nao pode") em vez de 404 ("nao existe") - a regra
    # de dominio ja barrava a acao, mas a diferenca de status confirmava a
    # existencia da conta a quem nao devia enxerga-la.
    alvo = get_object_or_404(escopo_do_painel(request.user).usuarios(), pk=pk)
    try:
        desativar_usuario(
            alvo=alvo,
            ator=request.user,
            confirmacao=request.POST.get("confirmacao") == "on",
            motivo=request.POST.get("motivo", ""),
        )
    except DesativacaoNegada as erro:
        return HttpResponseBadRequest(str(erro))
    return redirect("painel-usuario", pk=alvo.pk)


@superadmin_required
@require_POST
def usuario_zerar_creditos(request, pk):
    alvo = get_object_or_404(Usuario, pk=pk)
    try:
        zerar_creditos_usuario(
            alvo=alvo,
            ator=request.user,
            confirmado=request.POST.get("confirmacao") == "on",
            motivo=request.POST.get("motivo", ""),
        )
    except (AlocacaoSemConfirmacaoError, SaldoJaZeradoError) as erro:
        return HttpResponseBadRequest(str(erro))
    return redirect("painel-usuario", pk=alvo.pk)


@painel_required
def uso(request):
    """Monitoramento de consumo, no recorte de quem esta olhando.

    Diretor ve as contas da propria escola em percentual; equipe interna ve
    todas as escolas e o custo em dolar por tras de cada fornecedor.
    """
    escopo = escopo_do_painel(request.user)
    ciclo = request.GET.get("ciclo", "").strip() or None
    contexto = {
        "escopo": escopo,
        "ciclo": ciclo or ciclo_atual(),
        "contas": consumo_por_conta(escopo, ciclo=ciclo),
        "fornecedores": consumo_por_fornecedor(escopo, ciclo=ciclo),
        "contratos": contratos_para_o_painel(escopo),
    }
    return render(request, "painel_admin/uso.html", contexto)
