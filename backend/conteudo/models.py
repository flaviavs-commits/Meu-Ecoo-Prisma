from django.db import models

from .excecoes import ConteudoEstadoError


class OrigemConteudo(models.TextChoices):
    MANUAL = "MANUAL", "Manual"
    IA = "IA", "Inteligencia artificial"


class StatusConteudo(models.TextChoices):
    RASCUNHO = "RASCUNHO", "Rascunho"
    OFICIAL = "OFICIAL", "Oficial"
    ARQUIVADO = "ARQUIVADO", "Arquivado"


class Material(models.Model):
    instituicao = models.ForeignKey("contas.Instituicao", on_delete=models.PROTECT, related_name="materiais")
    turma = models.ForeignKey("academico.Turma", on_delete=models.PROTECT, related_name="materiais", null=True, blank=True)
    disciplina = models.ForeignKey("academico.Disciplina", on_delete=models.PROTECT, related_name="materiais", null=True, blank=True)
    arquivo = models.ForeignKey("arquivos.Arquivo", on_delete=models.PROTECT, related_name="materiais", null=True, blank=True)
    autor = models.ForeignKey("contas.Usuario", on_delete=models.PROTECT, related_name="materiais_criados")
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    origem = models.CharField(max_length=10, choices=OrigemConteudo.choices)
    status = models.CharField(max_length=10, choices=StatusConteudo.choices, default=StatusConteudo.RASCUNHO)
    revisado_por = models.ForeignKey("contas.Usuario", on_delete=models.PROTECT, related_name="materiais_revisados", null=True, blank=True)
    revisado_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.status == StatusConteudo.OFICIAL and not getattr(self, "_permitir_oficializacao", False):
            raise ConteudoEstadoError("Conteudo oficial so nasce pela acao de oficializacao.")
        super().save(*args, **kwargs)


class Prova(models.Model):
    instituicao = models.ForeignKey("contas.Instituicao", on_delete=models.PROTECT, related_name="provas")
    turma = models.ForeignKey("academico.Turma", on_delete=models.PROTECT, related_name="provas")
    disciplina = models.ForeignKey("academico.Disciplina", on_delete=models.PROTECT, related_name="provas")
    autor = models.ForeignKey("contas.Usuario", on_delete=models.PROTECT, related_name="provas_criadas")
    titulo = models.CharField(max_length=200)
    origem = models.CharField(max_length=10, choices=OrigemConteudo.choices)
    status = models.CharField(max_length=10, choices=StatusConteudo.choices, default=StatusConteudo.RASCUNHO)
    revisado_por = models.ForeignKey("contas.Usuario", on_delete=models.PROTECT, related_name="provas_revisadas", null=True, blank=True)
    revisado_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.status == StatusConteudo.OFICIAL and not getattr(self, "_permitir_oficializacao", False):
            raise ConteudoEstadoError("Prova oficial so nasce pela acao de oficializacao.")
        super().save(*args, **kwargs)


class Questao(models.Model):
    prova = models.ForeignKey(Prova, on_delete=models.PROTECT, related_name="questoes")
    ordem = models.PositiveIntegerField(default=1)
    enunciado = models.TextField()
    alternativas = models.JSONField(default=list, blank=True)
    gabarito = models.TextField()

    class Meta:
        ordering = ["ordem", "id"]
        constraints = [
            models.UniqueConstraint(fields=["prova", "ordem"], name="conteudo_ordem_questao_unica")
        ]
