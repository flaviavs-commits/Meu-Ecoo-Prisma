from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.core.validators import validate_email

from contas.models import Instituicao, Perfil
from contas.models import Usuario
from creditos.models import Lancamento, TipoLancamento


class Command(BaseCommand):
    help = "Cria uma instituicao, seu diretor e o credito inicial de forma transacional."

    def add_arguments(self, parser):
        parser.add_argument("--nome", required=True)
        parser.add_argument("--documento", required=True)
        parser.add_argument("--diretor-email", required=True)
        parser.add_argument("--diretor-nome", required=True)
        parser.add_argument("--creditos-iniciais", required=True)

    def handle(self, *args, **options):
        nome = options["nome"].strip()
        documento = options["documento"].strip()
        email = options["diretor_email"].strip().lower()
        diretor_nome = options["diretor_nome"].strip()
        try:
            creditos = Decimal(str(options["creditos_iniciais"]))
        except (InvalidOperation, TypeError):
            raise CommandError("creditos-iniciais deve ser um numero decimal valido.")
        if not nome or not documento or not email or not diretor_nome:
            raise CommandError("nome, documento, diretor-email e diretor-nome sao obrigatorios.")
        try:
            validate_email(email)
        except ValidationError as erro:
            raise CommandError("diretor-email deve ser um e-mail valido.") from erro
        if creditos < 0:
            raise CommandError("creditos-iniciais nao pode ser negativo.")

        try:
            with transaction.atomic():
                if Instituicao.objects.filter(documento=documento).exists():
                    raise CommandError(f"Ja existe uma instituicao com o documento {documento}.")
                if Usuario.objects.filter(email=email).exists():
                    raise CommandError(f"Ja existe um usuario com o e-mail {email}.")
                instituicao = Instituicao.objects.create(nome=nome, documento=documento)
                diretor = Usuario.objects.create(
                    email=email,
                    first_name=diretor_nome,
                    instituicao=instituicao,
                    perfil=Perfil.DIRETOR,
                    ativo=True,
                    is_active=True,
                    is_staff=False,
                )
                diretor.set_unusable_password()
                diretor.save(update_fields=["password"])
                if creditos:
                    Lancamento.objects.create(
                        instituicao=instituicao,
                        tipo=TipoLancamento.CREDITO,
                        quantidade=creditos,
                        motivo="credito inicial do onboarding",
                    )
        except IntegrityError as erro:
            raise CommandError("Nao foi possivel criar a instituicao: documento ou e-mail ja existe.") from erro

        self.stdout.write(
            self.style.SUCCESS(
                f"Instituicao criada: {instituicao.pk}; diretor criado: {diretor.pk}; "
                "senha ainda nao definida."
            )
        )
