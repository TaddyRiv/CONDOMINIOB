from django.core.management.base import BaseCommand
from django.db import transaction
import random

from app.models.apartamento import Apartamento

class Command(BaseCommand):
    help = "Siembra datos de prueba: crea apartamentos."  

    def add_arguments(self, parser):
        parser.add_argument(
            "--apartamentos",
            type=int,
            default=40,
            help="Número de apartamentos a crear (por defecto 40)."
        )
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Borra todos los apartamentos existentes antes de sembrar."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        n_apts = options['apartamentos']
        if options['clean']:
            self.stdout.write(self.style.WARNING("Borrando todos los apartamentos existentes..."))
            Apartamento.objects.all().delete()

        self.stdout.write(self.style.MIGRATE_HEADING(f"Creando {n_apts} apartamentos..."))
        apts = []
        for i in range(1, n_apts + 1):
            numero = f"A-{100 + i}"
            bloque = random.choice(["A", "B", "C", "D"])
            apts.append(Apartamento(numero=numero, bloque=bloque, estado="DISPONIBLE"))

        Apartamento.objects.bulk_create(apts, ignore_conflicts=True)
        total = Apartamento.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Total de apartamentos en BD: {total}"))
