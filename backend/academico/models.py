from django.db import models


class OrigemNota(models.TextChoices):
    MANUAL = "MANUAL", "Manual"
    IA = "IA", "Inteligencia artificial"


class Turma(models.Model):
    instituicao = models.ForeignKey("contas.Instituicao", on_delete=models.PROTECT, related_name="turmas")
    nome = models.CharField(max_length=120, default="Turma")
    disciplina = models.ForeignKey(
        "academico.Disciplina",
        on_delete=models.PROTECT,
        related_name="turmas",
        null=True,
        blank=True,
    )
    professor_responsavel = models.ForeignKey(
        "contas.Usuario",
        on_delete=models.PROTECT,
        related_name="turmas_responsavel",
        null=True,
        blank=True,
    )


class Disciplina(models.Model):
    instituicao = models.ForeignKey(
        "contas.Instituicao", on_delete=models.PROTECT, related_name="disciplinas"
    )
    nome = models.CharField(max_length=120)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["instituicao", "nome"], name="academico_disciplina_unica_instituicao"
            )
        ]


class ConfiguracaoNota(models.Model):
    instituicao = models.OneToOneField(
        "contas.Instituicao", on_delete=models.CASCADE, related_name="config_nota"
    )
    nota_minima = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    nota_maxima = models.DecimalField(max_digits=6, decimal_places=2, default=10)


class Matricula(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.PROTECT, related_name="matriculas")
    aluno = models.ForeignKey(
        "contas.Usuario", on_delete=models.PROTECT, related_name="matriculas"
    )
    entrou_em = models.DateField(auto_now_add=True)
    saiu_em = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["turma", "aluno"],
                condition=models.Q(saiu_em__isnull=True),
                name="academico_matricula_ativa_unica",
            )
        ]


class Nota(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.PROTECT, related_name="notas")
    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.PROTECT, related_name="notas"
    )
    aluno = models.ForeignKey("contas.Usuario", on_delete=models.PROTECT, related_name="notas")
    avaliacao = models.CharField(max_length=120)
    valor = models.DecimalField(max_digits=6, decimal_places=2)
    origem = models.CharField(max_length=10, choices=OrigemNota.choices, default=OrigemNota.MANUAL)
    oficial = models.BooleanField(default=False)
    criado_por = models.ForeignKey(
        "contas.Usuario", on_delete=models.PROTECT, related_name="notas_criadas"
    )
    alterado_por = models.ForeignKey(
        "contas.Usuario", on_delete=models.PROTECT, related_name="notas_alteradas", null=True, blank=True
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    alterado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["turma", "disciplina", "aluno", "avaliacao"],
                name="academico_nota_unica_avaliacao",
            ),
            models.CheckConstraint(
                condition=models.Q(valor__gte=0) & models.Q(valor__lte=10),
                name="academico_nota_entre_zero_e_dez",
            ),
        ]


class Falta(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.PROTECT, related_name="faltas")
    aluno = models.ForeignKey("contas.Usuario", on_delete=models.PROTECT, related_name="faltas")
    data = models.DateField()
    justificada = models.BooleanField(default=False)
    motivo = models.CharField(max_length=240, blank=True)
    criado_por = models.ForeignKey(
        "contas.Usuario", on_delete=models.PROTECT, related_name="faltas_criadas", null=True, blank=True
    )
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["turma", "aluno", "data"], name="academico_falta_unica_dia"
            )
        ]
