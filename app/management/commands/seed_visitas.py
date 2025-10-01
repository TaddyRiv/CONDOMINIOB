
import random
from django.core.management.base import BaseCommand
from faker import Faker
from app.models.apartamento import Apartamento
from app.models.vehiculo import Vehiculo
from app.models.visitante import Visitante
from app.models.visita import Visita
from app.models.usuario import Usuario

fake = Faker("es_ES")

class Command(BaseCommand):
    help = "Seed de vehículos, visitantes y visitas"

    def handle(self, *args, **options):
        # Obtener apartamentos
        apartamentos = list(Apartamento.objects.all())
        if not apartamentos:
            self.stdout.write(self.style.ERROR("⚠️ No hay apartamentos creados."))
            return

        # Crear 2 vehículos por apartamento
        for apto in apartamentos:
            for i in range(2):
                placa = f"{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}{fake.random_number(digits=3)}{fake.random_uppercase_letter()}"
                Vehiculo.objects.get_or_create(
                    placa=placa,
                    defaults={
                        "descripcion": fake.color_name() + " " + fake.word(),
                        "apartamento": apto,
                        "pase_conocido": True,
                        "activo": True,
                    },
                )
        self.stdout.write(self.style.SUCCESS(f"🚗 Vehículos creados: {Vehiculo.objects.count()}"))

        # Crear visitantes
        for _ in range(50):
            Visitante.objects.get_or_create(
                ci=fake.unique.random_number(digits=8),
                defaults={
                    "nombre": fake.name(),
                    "celular": fake.phone_number(),
                    "activo": True,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"🙋 Visitantes creados: {Visitante.objects.count()}"))

        # Crear visitas
        guardias = list(Usuario.objects.filter(rol="EMPLEADO")) or [None]
        for _ in range(100):
            visitante = random.choice(Visitante.objects.all())
            apto = random.choice(apartamentos)
            vehiculo = random.choice(list(apto.vehiculos.all()) + [None])
            registrado_por = random.choice(guardias)

            Visita.objects.create(
                visitante=visitante,
                apartamento=apto,
                vehiculo=vehiculo,
                detalle=fake.sentence(),
                registrado_por=registrado_por,
            )
        self.stdout.write(self.style.SUCCESS(f"📋 Visitas creadas: {Visita.objects.count()}"))
