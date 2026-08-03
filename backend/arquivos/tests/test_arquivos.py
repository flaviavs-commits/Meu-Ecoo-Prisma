import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from arquivos.excecoes import (
    ArquivoCotaExcedidaError,
    ArquivoTamanhoExcedidoError,
    ArquivoTipoNaoPermitidoError,
)
from arquivos.servico import enviar_arquivo

pytestmark = pytest.mark.django_db


def pdf(nome="trabalho.pdf", conteudo=b"%PDF-1.7\nconteudo"):
    return SimpleUploadedFile(nome, conteudo, content_type="application/octet-stream")


def cliente(usuario=None):
    api = APIClient()
    if usuario:
        api.force_authenticate(user=usuario)
    return api


def test_upload_valido_cria_registro_e_guarda_no_storage(instituicao, aluno):
    registro = enviar_arquivo(instituicao=instituicao, enviado_por=aluno, arquivo=pdf())

    assert registro.tipo_mime == "application/pdf"
    assert registro.tamanho_bytes > 0
    assert registro.arquivo.storage.exists(registro.arquivo.name)
    assert str(instituicao.id) in registro.arquivo.name


def test_nome_com_path_traversal_nao_escapa_da_pasta(instituicao, aluno, media_root):
    registro = enviar_arquivo(
        instituicao=instituicao,
        enviado_por=aluno,
        arquivo=pdf("../../../etc/passwd.pdf"),
    )

    caminho = (media_root / registro.arquivo.name).resolve()
    assert caminho.is_relative_to(media_root.resolve())
    assert ".." not in registro.arquivo.name


def test_executavel_renomeado_para_pdf_e_recusado(instituicao, aluno):
    with pytest.raises(ArquivoTipoNaoPermitidoError):
        enviar_arquivo(
            instituicao=instituicao,
            enviado_por=aluno,
            arquivo=pdf("virus.pdf", b"MZ\x90\x00executavel"),
        )


def test_arquivo_acima_do_limite_e_recusado(instituicao, aluno, settings):
    settings.ARQUIVO_MAX_BYTES = 4

    with pytest.raises(ArquivoTamanhoExcedidoError):
        enviar_arquivo(instituicao=instituicao, enviado_por=aluno, arquivo=pdf())


def test_cota_da_instituicao_e_respeitada(instituicao, aluno, settings):
    settings.ARQUIVO_COTA_INSTITUICAO_BYTES = 20
    enviar_arquivo(instituicao=instituicao, enviado_por=aluno, arquivo=pdf("um.pdf"))

    with pytest.raises(ArquivoCotaExcedidaError):
        enviar_arquivo(instituicao=instituicao, enviado_por=aluno, arquivo=pdf("dois.pdf"))


def test_download_de_outra_instituicao_responde_404(instituicao, aluno, outro_aluno):
    registro = enviar_arquivo(instituicao=instituicao, enviado_por=aluno, arquivo=pdf())

    resposta = cliente(outro_aluno).get(f"/api/v1/arquivos/{registro.id}/download/")

    assert resposta.status_code == 404


def test_download_sem_autenticacao_responde_401(instituicao, aluno):
    registro = enviar_arquivo(instituicao=instituicao, enviado_por=aluno, arquivo=pdf())

    resposta = cliente().get(f"/api/v1/arquivos/{registro.id}/download/")

    assert resposta.status_code == 401


def test_download_e_attachment_e_usa_nosniff(instituicao, aluno):
    registro = enviar_arquivo(instituicao=instituicao, enviado_por=aluno, arquivo=pdf())

    resposta = cliente(aluno).get(f"/api/v1/arquivos/{registro.id}/download/")

    assert resposta.status_code == 200
    assert resposta["Content-Disposition"].startswith("attachment;")
    assert resposta["X-Content-Type-Options"] == "nosniff"


def test_dois_uploads_com_mesmo_nome_nao_se_sobrescrevem(instituicao, aluno):
    primeiro = enviar_arquivo(instituicao=instituicao, enviado_por=aluno, arquivo=pdf())
    segundo = enviar_arquivo(instituicao=instituicao, enviado_por=aluno, arquivo=pdf())

    assert primeiro.arquivo.name != segundo.arquivo.name
