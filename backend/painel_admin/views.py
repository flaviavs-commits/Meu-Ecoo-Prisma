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
from contas.models import Instituicao, Perfil, TipoInstituicao
from creditos.excecoes import AlocacaoSemConfirmacaoError
from creditos.saldo import saldo_usuario

from .permissoes import exige_superadmin
from .forms.conta_teste import ContaTesteForm
from .forms.editar_instituicao import InstituicaoEdicaoForm
from .forms.editar_usuario import UsuarioEdicaoForm
from .forms.instituicao import InstituicaoForm
from .services.alterar_perfil import MotivoObrigatorio, PerfilInvalido, alterar_perfil
from .services.arquivar_instituicao import ArquivamentoInstituicaoNegado, arquivar_instituicao
from .services.criar_conta_teste import ContaTesteJaExisteError, criar_conta_teste
from .services.criar_instituicao import InstituicaoJaExisteError, criar_instituicao
from .services.editar_instituicao import InstituicaoEdicaoNegada, editar_instituicao
from .services.editar_usuario import UsuarioEdicaoNegada, editar_usuario
from .services.zerar_creditos import SaldoJaZeradoError, zerar_creditos_usuario


Usuario = get_user_model()


def superadmin_required(view):
    return login_required(exige_superadmin(view))


@superadmin_required
def dashboard(request):
    contexto = {
        "usuarios": Usuario.objects.count(),
        "instituicoes": Instituicao.objects.count(),
        "auditorias": RegistroDeAuditoria.objects.count(),
        "recentes": RegistroDeAuditoria.objects.select_related("ator").order_by("-criado_em")[:12],
    }
    return render(request, "painel_admin/dashboard.html", contexto)


@superadmin_required
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

    contexto = {
        "formulario": formulario,
        "instituicoes": Instituicao.objects.order_by("nome")[:100],
    }
    return render(request, "painel_admin/instituicoes.html", contexto)


@superadmin_required
def instituicao(request, pk):
    alvo = get_object_or_404(Instituicao, pk=pk)
    formulario = InstituicaoEdicaoForm(
        initial={"nome": alvo.nome, "documento": alvo.documento or ""}
    )
    return render(request, "painel_admin/instituicao.html", {"alvo": alvo, "formulario": formulario})


@require_POST
@superadmin_required
def instituicao_editar(request, pk):
    alvo = get_object_or_404(Instituicao, pk=pk)
    if alvo.tipo == TipoInstituicao.MANTENEDORA:
        return HttpResponseBadRequest("A instituição Vitis Souls não pode ser editada por este fluxo.")
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


@require_POST
@superadmin_required
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


@superadmin_required
def usuarios(request):
    consulta = request.GET.get("q", "").strip()
    perfil = request.GET.get("perfil", "").strip()
    queryset = Usuario.objects.select_related("instituicao").order_by("email")
    if consulta:
        queryset = queryset.filter(Q(email__icontains=consulta) | Q(first_name__icontains=consulta))
    if perfil in Perfil.values:
        queryset = queryset.filter(perfil=perfil)
    contexto = {"usuarios": queryset[:100], "consulta": consulta, "perfil": perfil, "perfis": Perfil.choices}
    return render(request, "painel_admin/usuarios.html", contexto)


@superadmin_required
def usuario(request, pk):
    alvo = get_object_or_404(Usuario.objects.select_related("instituicao"), pk=pk)
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
        "alvo": alvo,
        "perfis": Perfil.choices,
        "saldo": saldo_usuario(alvo.pk),
        "formulario_edicao": formulario_edicao,
    }
    return render(request, "painel_admin/usuario.html", contexto)


@require_POST
@superadmin_required
def usuario_editar(request, pk):
    alvo = get_object_or_404(Usuario.objects.select_related("instituicao"), pk=pk)
    formulario = UsuarioEdicaoForm(alvo=alvo, data=request.POST)
    if not formulario.is_valid():
        contexto = {
            "alvo": alvo,
            "perfis": Perfil.choices,
            "saldo": saldo_usuario(alvo.pk),
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
            "saldo": saldo_usuario(alvo.pk),
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
    acoes_disponiveis = (
        RegistroDeAuditoria.objects.order_by("acao").values_list("acao", flat=True).distinct()
    )
    pagina = Paginator(queryset, 25).get_page(request.GET.get("pagina"))
    contexto = {"pagina": pagina, "acao": acao, "consulta": consulta, "acoes": acoes_disponiveis}
    return render(request, "painel_admin/registros.html", contexto)


@require_POST
@superadmin_required
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


@require_POST
@superadmin_required
def usuario_desativar(request, pk):
    alvo = get_object_or_404(Usuario, pk=pk)
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


@require_POST
@superadmin_required
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
