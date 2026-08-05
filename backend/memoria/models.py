from django.db import models


class PapelMensagem(models.TextChoices):
    ALUNO = "ALUNO", "Aluno"
    TUTOR = "TUTOR", "Tutor"


class EstiloTutor(models.TextChoices):
    SOCRATICO = "SOCRATICO", "Socratico"
    DIRETO = "DIRETO", "Direto"


class DificuldadeTutor(models.TextChoices):
    BASICO = "BASICO", "Basico"
    MEDIO = "MEDIO", "Medio"
    DIFICIL = "DIFICIL", "Dificil"


class TamanhoRespostaTutor(models.TextChoices):
    CURTA = "CURTA", "Curta"
    DETALHADA = "DETALHADA", "Detalhada"


class MemoriaImutavelError(Exception):
    """Levantada quando uma memoria consolidada existente seria alterada."""


class Conversa(models.Model):
    aluno = models.ForeignKey(
        "contas.Usuario", on_delete=models.PROTECT, related_name="conversas_tutor"
    )
    titulo = models.CharField(max_length=200, blank=True)
    disciplina = models.CharField(max_length=120, blank=True)
    topico = models.CharField(max_length=160, blank=True)
    retencao_expira_em = models.DateTimeField(null=True, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criada_em", "id"]


class Mensagem(models.Model):
    conversa = models.ForeignKey(
        Conversa, on_delete=models.CASCADE, related_name="mensagens"
    )
    papel = models.CharField(max_length=5, choices=PapelMensagem.choices)
    conteudo = models.TextField()
    chamada_ia = models.ForeignKey(
        "ia.ChamadaIA",
        on_delete=models.SET_NULL,
        related_name="mensagens_tutor",
        null=True,
        blank=True,
    )
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criada_em", "id"]
        indexes = [models.Index(fields=["conversa", "criada_em"])]


class ConfiguracaoTutor(models.Model):
    usuario = models.OneToOneField(
        "contas.Usuario", on_delete=models.CASCADE, related_name="configuracao_tutor"
    )
    estilo = models.CharField(
        max_length=10, choices=EstiloTutor.choices, default=EstiloTutor.SOCRATICO
    )
    dificuldade = models.CharField(
        max_length=10, choices=DificuldadeTutor.choices, default=DificuldadeTutor.MEDIO
    )
    foco_exame = models.CharField(max_length=40, default="ENEM")
    tamanho_resposta = models.CharField(
        max_length=12,
        choices=TamanhoRespostaTutor.choices,
        default=TamanhoRespostaTutor.CURTA,
    )
    correcao_comentada = models.BooleanField(default=True)
    foco_dificuldades = models.BooleanField(default=True)
    resposta_audio = models.BooleanField(default=False)
    usar_arquivos_contexto = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)


class MemoriaConsolidada(models.Model):
    aluno = models.ForeignKey(
        "contas.Usuario", on_delete=models.PROTECT, related_name="memorias_tutor"
    )
    disciplina = models.CharField(max_length=120, blank=True)
    topico = models.CharField(max_length=160, blank=True)
    resumo = models.TextField()
    periodo_inicio = models.DateTimeField(null=True, blank=True)
    periodo_fim = models.DateTimeField(null=True, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criada_em", "-id"]
        indexes = [
            models.Index(fields=["aluno", "disciplina", "topico", "-criada_em"]),
        ]

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise MemoriaImutavelError(
                "Memoria consolidada e imutavel: consolide novamente em novo registro."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise MemoriaImutavelError("Memoria consolidada nao e apagada por convencao.")
