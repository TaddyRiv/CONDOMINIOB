from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import calendar
import random
import datetime

from app.models.apartamento import Apartamento
from app.models.servicio import Servicio
from app.models.cargo import Cargo
from app.models.cargo_servicio import CargoServicio
from app.models.pago import Pago
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Siembra servicios, genera cargos mensuales por apartamento y crea pagos (aprobados/pendientes)."

    def add_arguments(self, parser):
        parser.add_argument("--anio", type=int, default=timezone.now().year)
        parser.add_argument("--mes", type=int, default=timezone.now().month)
        parser.add_argument("--servicios", nargs="*", default=["Mantenimiento", "Limpieza", "Agua", "Gas"])
        parser.add_argument("--crear_pagos", action="store_true", help="Genera pagos aleatorios.")
        parser.add_argument("--ratio_pagados", type=float, default=0.5, help="Proporción de cargos con pagos aprobados (0..1).")
        parser.add_argument("--admin_email", type=str, default=None, help="Usuario que aparecerá como 'creado_por' en Cargo y verificador de pagos.")

    def _periodo_date(self, anio, mes):
        # Usamos el primer día del mes
        return datetime.date(anio, mes, 1)

    def _ensure_servicios(self, nombres):
        creados = []
        for n in nombres:
            s, _ = Servicio.objects.get_or_create(nombre=n, defaults={
                "descripcion": f"Servicio de {n.lower()}",
                "precio": Decimal(random.choice([30, 40, 50, 60, 75, 100])),
                "activo": True,
            })
            creados.append(s)
        return creados

    @transaction.atomic
    def handle(self, *args, **opts):
        anio = opts["anio"]
        mes = opts["mes"]
        periodo = self._periodo_date(anio, mes)

        admin_user = None
        if opts["admin_email"]:
            admin_user = User.objects.filter(email=opts["admin_email"]).first()

        self.stdout.write(self.style.MIGRATE_HEADING("Asegurando servicios..."))
        servicios = self._ensure_servicios(opts["servicios"])

        apts = list(Apartamento.objects.all())
        if not apts:
            self.stdout.write(self.style.ERROR("No hay apartamentos. Crea apartamentos antes de generar cargos."))
            return

        self.stdout.write(self.style.MIGRATE_HEADING(f"Creando cargos del periodo {periodo:%Y-%m}..."))
        cargos_creados = 0
        for apt in apts:
            cargo, created = Cargo.objects.get_or_create(
                apartamento=apt, periodo=periodo,
                defaults={"descripcion": f"Cargo mensual {periodo:%Y-%m}", "creado_por": admin_user}
            )
            if created:
                cargos_creados += 1

            # Limpia detalles previos para idempotencia (opcional)
            cargo.detalles.all().delete()

            # Agrega de 1 a 3 servicios por cargo
            num_serv = random.randint(1, min(3, len(servicios)))
            seleccion = random.sample(servicios, num_serv)
            for s in seleccion:
                # Permitimos personalizar precio_unitario o usar s.precio por defecto
                CargoServicio.objects.create(
                    cargo=cargo,
                    servicio=s,
                    cantidad=Decimal("1.00"),
                    precio_unitario=s.precio,
                )
            # recomputar_total ya se llama dentro de CargoServicio.save()

        self.stdout.write(self.style.SUCCESS(f"Cargos creados/asegurados: {cargos_creados}"))

        if not opts["crear_pagos"]:
            self.stdout.write(self.style.WARNING("No se crearon pagos. Usa --crear_pagos para generarlos."))
            return

        self.stdout.write(self.style.MIGRATE_HEADING("Generando pagos..."))
        cargos = list(Cargo.objects.filter(periodo=periodo))
        if not cargos:
            self.stdout.write(self.style.ERROR("No hay cargos del periodo."))
            return

        # Tomamos un pagador cualquiera (usuario residente/dueno). Ajusta filtro si quieres.
        posibles_pagadores = list(User.objects.all()[:500])
        if not posibles_pagadores:
            self.stdout.write(self.style.ERROR("No hay usuarios para asignar como pagadores."))
            return

        aprobados_obj = []
        pendientes_obj = []
        for cargo in cargos:
            # Decide si este cargo será “pagado” o “pendiente”
            pagado = random.random() < float(opts["ratio_pagados"])

            if pagado:
                # Crea 1 o 2 pagos APROBADOS que sumen (aprox) el total
                restante = cargo.total
                n = random.choice([1, 2])
                montos = []
                if n == 1:
                    montos = [restante]
                else:
                    p1 = (restante * Decimal("0.5")).quantize(Decimal("0.01"))
                    p2 = (restante - p1).quantize(Decimal("0.01"))
                    montos = [p1, p2]

                for m in montos:
                    pagador = random.choice(posibles_pagadores)
                    p = Pago(
                        cargo=cargo,
                        tipo=random.choice([Pago.Tipo.QR, Pago.Tipo.EFECTIVO]),
                        pagador=pagador,
                        monto=m,
                        estado=Pago.Estado.APROBADO,
                        verificado_por=admin_user,
                        fecha_verificacion=timezone.now(),
                        observacion="Pago de prueba aprobado",
                    )
                    aprobados_obj.append(p)
            else:
                # Crea un pago PENDIENTE (no afecta saldo hasta aprobar)
                pagador = random.choice(posibles_pagadores)
                m = (cargo.total * Decimal(random.choice([0.3, 0.5, 0.8]))).quantize(Decimal("0.01"))
                p = Pago(
                    cargo=cargo,
                    tipo=random.choice([Pago.Tipo.QR, Pago.Tipo.EFECTIVO]),
                    pagador=pagador,
                    monto=m,
                    estado=Pago.Estado.PENDIENTE,
                    observacion="Pago pendiente de verificación",
                )
                pendientes_obj.append(p)

        # Bulk create
        if aprobados_obj:
            Pago.objects.bulk_create(aprobados_obj)
        if pendientes_obj:
            Pago.objects.bulk_create(pendientes_obj)

        # Reaplicar totales por si algún cargo no llamó aún aplicar_pago_aprobado
        for cargo in cargos:
            cargo.aplicar_pago_aprobado()

        self.stdout.write(self.style.SUCCESS(
            f"Pagos creados -> Aprobados: {len(aprobados_obj)} | Pendientes: {len(pendientes_obj)}"
        ))
        self.stdout.write(self.style.SUCCESS("Listo ✅"))
