from django.core.files.storage import default_storage


class StorageAdapter:
    """Fachada minima para trocar disco por storage de nuvem sem alterar o dominio."""

    def save(self, nome, conteudo):
        return default_storage.save(nome, conteudo)

    def delete(self, nome):
        default_storage.delete(nome)

    def open(self, nome, modo="rb"):
        return default_storage.open(nome, modo)
