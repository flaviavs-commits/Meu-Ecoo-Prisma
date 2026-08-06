from django.db import models


class Aviso(models.Model):
    """Comunicado do professor para os alunos de uma turma.

    Destinatario e a turma, nao o aluno: quem le e quem esta matriculado nela
    no momento da leitura. Assim uma matricula nova ja enxerga o historico e
    uma matricula encerrada para de enxergar, sem precisar reescrever o aviso.
    """

    instituicao = models.ForeignKey(
        "contas.Instituicao", on_delete=models.PROTECT, related_name="avisos"
    )
    turma = models.ForeignKey(
        "academico.Turma", on_delete=models.PROTECT, related_name="avisos"
    )
    autor = models.ForeignKey(
        "contas.Usuario", on_delete=models.PROTECT, related_name="avisos_enviados"
    )
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    # Prazo opcional: o aviso pode ser uma atividade proposta com data, no
    # mesmo espirito de `conteudo.Material.prazo_entrega`.
    prazo_entrega = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em", "-id"]
        indexes = [models.Index(fields=["turma", "criado_em"])]

    def __str__(self):
        return self.titulo
