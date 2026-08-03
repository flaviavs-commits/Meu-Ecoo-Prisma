from rest_framework.permissions import BasePermission


class PerfilPermission(BasePermission):
    perfil = None

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.perfil == self.perfil)


class EAluno(PerfilPermission):
    perfil = "ALUNO"


class EProfessor(PerfilPermission):
    perfil = "PROFESSOR"


class EDiretor(PerfilPermission):
    perfil = "DIRETOR"
