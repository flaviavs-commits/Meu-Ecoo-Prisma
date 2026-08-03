from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from contas.auditoria import RegistroDeAuditoria
from contas.models import Instituicao, Perfil

from .permissoes import exige_superadmin
from .services.alterar_perfil import MotivoObrigatorio, PerfilInvalido, alterar_perfil


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
    return render(request, "painel_admin/usuario.html", {"alvo": alvo, "perfis": Perfil.choices})


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
