"""Fixtures compartilhadas pelos testes de limites.

`test_concorrencia.py` pedia `instituicao`/`aluno` e nao existia conftest neste
app: as fixtures viviam dentro de `test_cota.py`, e fixture declarada num
modulo de teste nao e visivel para outro. O `skipif` de SQLite escondia o erro,
entao o teste de concorrencia nunca rodou em lugar nenhum.
"""

import pytest
from django.contrib.auth import get_user_model

from contas.models import Instituicao, Perfil


@pytest.fixture
def instituicao(db):
    return Instituicao.objects.create(
        nome="Escola Limites", documento="00.000.000/0001-31"
    )


@pytest.fixture
def aluno(db, instituicao):
    return get_user_model().objects.create_user(
        email="aluno-limites@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.ALUNO,
    )
