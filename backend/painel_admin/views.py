from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from contas.auditoria import RegistroDeAuditoria
from contas.desativacao import DesativacaoNegada, desativar_usuario
from contas.models import Instituicao, Perfil
from creditos.excecoes import AlocacaoSemConfirmacaoError
from creditos.saldo import saldo_usuario

from .permissoes import exige_superadmin
from .services.alterar_perfil import MotivoObrigatorio, PerfilInvalido, alterar_perfil
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
    contexto = {"alvo": alvo, "perfis": Perfil.choices, "saldo": saldo_usuario(alvo.pk)}
    return render(request, "painel_admin/usuario.html", contexto)


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
