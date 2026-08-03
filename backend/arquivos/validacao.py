import io
import zipfile


TIPOS_PERMITIDOS = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "audio/mpeg",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def detectar_mime(arquivo):
    inicio = arquivo.read(16)
    arquivo.seek(0)
    if inicio.startswith(b"%PDF-"):
        return "application/pdf"
    if inicio.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if inicio.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if inicio.startswith(b"ID3") or _parece_frame_mp3(inicio):
        return "audio/mpeg"
    if _e_docx(arquivo):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return None


def _parece_frame_mp3(inicio):
    return len(inicio) >= 2 and inicio[0] == 0xFF and (inicio[1] & 0xE0) == 0xE0


def _e_docx(arquivo):
    try:
        arquivo.seek(0)
        with zipfile.ZipFile(arquivo) as pacote:
            nomes = set(pacote.namelist())
            return "[Content_Types].xml" in nomes and "word/document.xml" in nomes
    except (zipfile.BadZipFile, OSError):
        return False
    finally:
        arquivo.seek(0)
