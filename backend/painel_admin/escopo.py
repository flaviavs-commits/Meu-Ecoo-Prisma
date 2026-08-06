"""O que cada tier enxerga dentro do painel.

O painel é o mesmo site para todo mundo; o que muda é o recorte. Em vez de
espalhar `if perfil == ...` por cada view, cada uma pergunta o escopo aqui e
usa as querysets que ele devolve. Assim existe **um** lugar onde o isolamento
entre escolas pode ser lido, revisado e testado.

| Tier | Alcance | Custo em dólar |
|------|---------|----------------|
| `PROVIDER` | todas as instituições | vê |
| `ADMINISTRADOR` | todas as instituições | vê |
| `DIRETOR` | só a própria escola | **não vê** |

O diretor não vê custo real de propósito: o contrato de produto com a escola é
percentual, e quanto a plataforma paga a cada fornecedor é assunto da
plataforma. Ele monitora o consumo das contas dele, na mesma régua que elas.
"""
from dataclasses import dataclass

from django.contrib.auth import get_user_model

from contas.models import Instituicao
from limites.models import ConsumoIA


@dataclass(frozen=True)
class EscopoDoPainel:
    usuario: object
    cross_tenant: bool
    ve_custo_real: bool
    pode_administrar_plataforma: bool

    @property
    def instituicao_id(self):
        """Instituição à qual o escopo está preso. `None` quando é cross-tenant."""
        return None if self.cross_tenant else self.usuario.instituicao_id

    def instituicoes(self):
        if self.cross_tenant:
            return Instituicao.objects.all()
        return Instituicao.objects.filter(pk=self.instituicao_id)

    def usuarios(self):
        queryset = get_user_model().objects.select_related("instituicao")
        if self.cross_tenant:
            return queryset
        # `instituicao_id` é anulável: sem esta guarda, um diretor sem
        # instituição casaria com todas as contas órfãs do sistema.
        if self.instituicao_id is None:
            return queryset.none()
        return queryset.filter(instituicao_id=self.instituicao_id)

    def consumos(self):
        queryset = ConsumoIA.objects.select_related("usuario")
        if self.cross_tenant:
            return queryset
        if self.instituicao_id is None:
            return queryset.none()
        return queryset.filter(instituicao_id=self.instituicao_id)


def escopo_do_painel(usuario):
    """Traduz o tier da conta logada no recorte que ela enxerga."""
    if getattr(usuario, "eh_provider", False):
        return EscopoDoPainel(
            usuario=usuario,
            cross_tenant=True,
            ve_custo_real=True,
            pode_administrar_plataforma=True,
        )
    if getattr(usuario, "eh_administrador", False):
        return EscopoDoPainel(
            usuario=usuario,
            cross_tenant=True,
            ve_custo_real=True,
            pode_administrar_plataforma=False,
        )
    return EscopoDoPainel(
        usuario=usuario,
        cross_tenant=False,
        ve_custo_real=False,
        pode_administrar_plataforma=False,
    )


def eh_diretor_de_escola(usuario) -> bool:
    return bool(
        getattr(usuario, "perfil", None) == "DIRETOR"
        and getattr(usuario, "ativo", False)
        and usuario.is_active
        and usuario.instituicao_id
    )


def pode_entrar_no_painel(usuario) -> bool:
    """Quem tem alguma leitura legítima no painel."""
    return bool(
        getattr(usuario, "eh_staff_interno", False) or eh_diretor_de_escola(usuario)
    )
