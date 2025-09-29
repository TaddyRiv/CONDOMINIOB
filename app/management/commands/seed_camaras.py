# app/management/commands/seed_camaras.py
from django.core.management.base import BaseCommand
from app.models import PuntoAcceso, Camara

class Command(BaseCommand):
    help = "Crea puntos de acceso y cámaras por defecto"

    def handle(self, *args, **kwargs):
        # Crear punto de acceso principal
        p, created = PuntoAcceso.objects.get_or_create(
            nombre="Entrada Principal",
            defaults={
                "ubicacion": "Puerta 1",
                "tipo": "PERSONA"
            }
        )

        # Crear cámaras vinculadas
        c1, _ = Camara.objects.get_or_create(
            nombre="Cámara Entrada",
            punto_acceso=p,
            defaults={"ubicacion": "Puerta 1"}
        )

        c2, _ = Camara.objects.get_or_create(
            nombre="Cámara Salida",
            punto_acceso=p,
            defaults={"ubicacion": "Puerta 1"}
        )

        self.stdout.write(self.style.SUCCESS(f"✅ Punto de acceso creado: {p.id}"))
        self.stdout.write(self.style.SUCCESS(f"✅ Cámara Entrada creada: {c1.id}"))
        self.stdout.write(self.style.SUCCESS(f"✅ Cámara Salida creada: {c2.id}"))
