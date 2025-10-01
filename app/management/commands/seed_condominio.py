# app/management/commands/seed_condominio.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from faker import Faker
import random
import datetime

from app.models.apartamento import Apartamento
from app.models.residencia import Residencia
from app.models.propiedad import Propiedad

User = get_user_model()
fake = Faker("es_ES")

def rand_date(start_year=2018, end_year=None):
    """Fecha aleatoria entre start_year y hoy."""
    end_year = end_year or timezone.now().year
    start = datetime.date(start_year, 1, 1)
    end = timezone.now().date()
    return fake.date_between(start_date=start, end_date=end)

class Command(BaseCommand):
    help = "Siembra datos de prueba: apartamentos, usuarios (RESIDENTE/DUEÑO), propiedades y residencias."

    def add_arguments(self, parser):
        parser.add_argument("--apartamentos", type=int, default=40)
        parser.add_argument("--residentes", type=int, default=100)
        parser.add_argument("--duenos", type=int, default=80)
        parser.add_argument("--password", type=str, default="12345678")
        parser.add_argument("--clean", action="store_true", help="Borra tablas objetivo antes de sembrar (¡CUIDADO!).")

    @transaction.atomic
    def handle(self, *args, **opts):
        n_apts = opts["apartamentos"]
        n_res = opts["residentes"]
        n_due = opts["duenos"]
        default_pwd = opts["password"]

        if opts["clean"]:
            self.stdout.write(self.style.WARNING("Borrando datos existentes…"))
            # Borra en orden seguro (FK)
            Residencia.objects.all().delete()
            Propiedad.objects.all().delete()
            Apartamento.objects.all().delete()
            # NO borramos usuarios admin existentes; solo usuarios de prueba creados por este seeder
            User.objects.filter(email__startswith="residente").delete()
            User.objects.filter(email__startswith="dueno").delete()

        # ---------- Apartamentos ----------
        self.stdout.write(self.style.MIGRATE_HEADING(f"Creando {n_apts} apartamentos…"))
        apts = []
        for i in range(1, n_apts + 1):
            numero = f"A-{100 + i}"          # A-101, A-102, …
            bloque = random.choice(["A", "B", "C", "D"])
            apts.append(Apartamento(numero=numero, bloque=bloque, estado="DISPONIBLE"))
        Apartamento.objects.bulk_create(apts, ignore_conflicts=True)
        apts = list(Apartamento.objects.all().order_by("numero"))
        if len(apts) < n_apts:
            self.stdout.write(self.style.WARNING(f"Había apartamentos previos. Usando {len(apts)} en total."))

        # ---------- Usuarios RESIDENTE ----------
        self.stdout.write(self.style.MIGRATE_HEADING(f"Creando {n_res} residentes…"))
        residentes = []
        for i in range(1, n_res + 1):
            email = f"residente{i}@demo.local"
            ci = f"7{i:07d}"
            user = User(
                email=email,
                username=f"residente{i}",
                ci=ci,
                rol="RESIDENTE",
                nombre=fake.name(),
                telefono=fake.msisdn()[:10],
                fecha_nacimiento=fake.date_of_birth(minimum_age=18, maximum_age=70),
            )
            user.set_password(default_pwd)
            residentes.append(user)
        User.objects.bulk_create(residentes, ignore_conflicts=True)
        residentes = list(User.objects.filter(email__startswith="residente").order_by("id"))

        # ---------- Usuarios DUEÑO ----------
        self.stdout.write(self.style.MIGRATE_HEADING(f"Creando {n_due} dueños…"))
        duenos = []
        for i in range(1, n_due + 1):
            email = f"dueno{i}@demo.local"
            ci = f"8{i:07d}"
            user = User(
                email=email,
                username=f"dueno{i}",
                ci=ci,
                rol="DUEÑO",
                nombre=fake.name(),
                telefono=fake.msisdn()[:10],
                fecha_nacimiento=fake.date_of_birth(minimum_age=18, maximum_age=70),
            )
            user.set_password(default_pwd)
            duenos.append(user)
        User.objects.bulk_create(duenos, ignore_conflicts=True)
        duenos = list(User.objects.filter(email__startswith="dueno").order_by("id"))

        # ---------- Propiedades y Residencias ----------
        # 40 propietarios activos (uno por apartamento) + 40 propietarios históricos
        activos = min(len(apts), len(duenos), 40)  # por si cambias los números
        self.stdout.write(self.style.MIGRATE_HEADING(f"Asignando {activos} propietarios activos (1 por apartamento)…"))

        propiedades_bulk = []
        residencias_bulk = []

        # Asigna 1 dueño activo a cada apto (sin romper uniq_propiedad_activa_por_apartamento)
        for apt, owner in zip(apts[:activos], duenos[:activos]):
            fi = rand_date(2020)
            propiedades_bulk.append(Propiedad(
                usuario=owner,
                apartamento=apt,
                fecha_inicio=fi,
                fecha_fin=None,  # activo
            ))
            # También residen en su mismo apartamento
            residencias_bulk.append(Residencia(
                usuario=owner,
                apartamento=apt,
                fecha_inicio=fi,
                fecha_fin=None,  # activa
            ))

        # Dueños restantes: propiedad HISTÓRICA y residencia ACTIVA en algún apto
        restantes = duenos[activos:]
        for owner in restantes:
            # Propiedad histórica en un apto aleatorio
            apt_hist = random.choice(apts)
            fi = rand_date(2019)
            ff = fi + datetime.timedelta(days=random.randint(120, 900))
            if ff >= timezone.now().date():
                ff = fi + datetime.timedelta(days=365)  # asegura histórico
            propiedades_bulk.append(Propiedad(
                usuario=owner,
                apartamento=apt_hist,
                fecha_inicio=fi,
                fecha_fin=ff,
            ))
            # Residencia actual en otro apto aleatorio
            apt_res = random.choice(apts)
            fr = rand_date(2022)
            residencias_bulk.append(Residencia(
                usuario=owner,
                apartamento=apt_res,
                fecha_inicio=fr,
                fecha_fin=None,  # activa
            ))

        # Residencias para los 100 RESIDENTES (todos activos, 1 por usuario)
        self.stdout.write(self.style.MIGRATE_HEADING(f"Asignando residencias a {len(residentes)} residentes…"))
        for r in residentes:
            apt = random.choice(apts)
            fi = rand_date(2022)
            residencias_bulk.append(Residencia(
                usuario=r,
                apartamento=apt,
                fecha_inicio=fi,
                fecha_fin=None,
            ))

        # Persistimos en BD
        self.stdout.write(self.style.MIGRATE_HEADING("Guardando Propiedades…"))
        Propiedad.objects.bulk_create(propiedades_bulk)

        self.stdout.write(self.style.MIGRATE_HEADING("Guardando Residencias…"))
        # Ojo: UniqueConstraint condicional en Residencia (activa por usuario) se respeta porque solo creamos 1 activa por usuario
        # Si existían residencias previas activas para algún usuario, puede fallar; en ese caso usa --clean
        Residencia.objects.bulk_create(residencias_bulk)

        # Opcional: marca estado de aptos con propietario activo como OCUPADO
        apts_con_dueno_activo = set(p.apartamento_id for p in Propiedad.objects.filter(fecha_fin__isnull=True))
        Apartamento.objects.filter(id__in=apts_con_dueno_activo).update(estado="OCUPADO")

        self.stdout.write(self.style.SUCCESS("Seed completado."))
        self.stdout.write(self.style.SUCCESS(f"Apartamentos: {Apartamento.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Residentes creados: {len(residentes)}"))
        self.stdout.write(self.style.SUCCESS(f"Dueños creados: {len(duenos)}"))
        self.stdout.write(self.style.SUCCESS(f"Propiedades totales: {Propiedad.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Residencias totales: {Residencia.objects.count()}"))
