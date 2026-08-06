from django.db import models

from .excecoes import ConteudoEstadoError


class OrigemConteudo(models.TextChoices):
    MANUAL = "MANUAL", "Manual"
    IA = "IA", "Inteligencia artificial"


class FormatoMaterial(models.TextChoices):
    MATERIAL = "MATERIAL", "Material"
    RESUMO = "RESUMO", "Resumo"
    FLASHCARDS = "FLASHCARDS", "Flashcards"
    AUDIO = "AUDIO", "Audio-revisao"
    IMPORTADO = "IMPORTADO", "Importado"


class StatusConteudo(models.TextChoices):
    RASCUNHO = "RASCUNHO", "Rascunho"
    OFICIAL = "OFICIAL", "Oficial"
    ARQUIVADO = "ARQUIVADO", "Arquivado"


class StatusSimulado(models.TextChoices):
    EM_ANDAMENTO = "EM_ANDAMENTO", "Em andamento"
    CONCLUIDO = "CONCLUIDO", "Concluido"


class Material(models.Model):
    instituicao = models.ForeignKey("contas.Instituicao", on_delete=models.PROTECT, related_name="materiais")
    turma = models.ForeignKey("academico.Turma", on_delete=models.PROTECT, related_name="materiais", null=True, blank=True)
    disciplina = models.ForeignKey("academico.Disciplina", on_delete=models.PROTECT, related_name="materiais", null=True, blank=True)
    arquivo = models.ForeignKey("arquivos.Arquivo", on_delete=models.PROTECT, related_name="materiais", null=True, blank=True)
    autor = models.ForeignKey("contas.Usuario", on_delete=models.PROTECT, related_name="materiais_criados")
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    formato = models.CharField(
        max_length=12, choices=FormatoMaterial.choices, default=FormatoMaterial.MATERIAL
    )
    origem = models.CharField(max_length=10, choices=OrigemConteudo.choices)
    chamada_ia = models.ForeignKey(
        "ia.ChamadaIA",
        on_delete=models.PROTECT,
        related_name="materiais_gerados",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=10, choices=StatusConteudo.choices, default=StatusConteudo.RASCUNHO)
    # Prazo da atividade proposta (trabalho, plano de aula, leitura). Nulo para
    # material de consulta, que nao se entrega.
    prazo_entrega = models.DateTimeField(null=True, blank=True)
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
    # Prazo de aplicacao da prova. Nulo enquanto o professor nao agenda.
    prazo_entrega = models.DateTimeField(null=True, blank=True)
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


class Simulado(models.Model):
    instituicao = models.ForeignKey(
        "contas.Instituicao", on_delete=models.PROTECT, related_name="simulados_alunos"
    )
    aluno = models.ForeignKey(
        "contas.Usuario", on_delete=models.PROTECT, related_name="simulados_alunos"
    )
    disciplina = models.CharField(max_length=120)
    estilo = models.CharField(max_length=40, default="ENEM")
    quantidade = models.PositiveSmallIntegerField()
    foco_dificuldades = models.BooleanField(default=True)
    correcao_comentada = models.BooleanField(default=True)
    status = models.CharField(
        max_length=12, choices=StatusSimulado.choices, default=StatusSimulado.EM_ANDAMENTO
    )
    resultado_percentual = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True
    )
    chamada_ia = models.ForeignKey(
        "ia.ChamadaIA",
        on_delete=models.PROTECT,
        related_name="simulados_gerados",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    concluido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-criado_em", "-id"]
        indexes = [models.Index(fields=["aluno", "status", "criado_em"])]


class QuestaoSimulado(models.Model):
    simulado = models.ForeignKey(Simulado, on_delete=models.CASCADE, related_name="questoes")
    ordem = models.PositiveSmallIntegerField()
    enunciado = models.TextField()
    alternativas = models.JSONField(default=list)
    gabarito = models.CharField(max_length=2)
    resposta = models.CharField(max_length=2, blank=True)

    class Meta:
        ordering = ["ordem", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["simulado", "ordem"], name="conteudo_ordem_questao_simulado_unica"
            )
        ]
