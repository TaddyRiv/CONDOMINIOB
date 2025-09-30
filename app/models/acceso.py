from django.db import models
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo



class PuntoAcceso(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    tipo = models.CharField(
        max_length=50,
        choices=[("VEHICULO", "Vehículo"), ("PERSONA", "Persona"), ("MIXTO", "Mixto")],
        default="MIXTO"
    )

    class Meta:
        db_table = "puntos_acceso"

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class Camara(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    punto_acceso = models.ForeignKey(
        PuntoAcceso, on_delete=models.CASCADE, related_name="camaras"
    )
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = "camaras"

    def __str__(self):
        return f"{self.nombre} - {self.ubicacion or ''}"


class Reconocimiento(models.Model):
    TIPOS = [("PLACA", "Placa"), ("ROSTRO", "Rostro")]

    tipo = models.CharField(max_length=10, choices=TIPOS)
    captura = models.ImageField(upload_to="reconocimientos/", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    camara = models.ForeignKey(Camara, on_delete=models.CASCADE, related_name="reconocimientos")

    # Integración con AWS Rekognition
    aws_face_id = models.CharField(max_length=200, blank=True, null=True)  # ID único de la colección
    confianza = models.FloatField(blank=True, null=True)  # porcentaje de similitud

    class Meta:
        db_table = "reconocimientos"

    def __str__(self):
        return f"{self.tipo} - {self.timestamp:%Y-%m-%d %H:%M}"


class IntentoAcceso(models.Model):
    RESULTADOS = [("ACEPTADO", "Aceptado"), ("DENEGADO", "Denegado")]

    reconocimiento = models.OneToOneField(
        Reconocimiento, on_delete=models.CASCADE, related_name="intento"
    )
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="intentos_acceso"
    )
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name="intentos_acceso"
    )
    punto_acceso = models.ForeignKey(  # 🔹 agregado
        PuntoAcceso, on_delete=models.CASCADE, related_name="intentos"
    )
    resultado = models.CharField(max_length=10, choices=RESULTADOS)
    motivo = models.CharField(max_length=255, blank=True, null=True)
    accion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "intentos_acceso"

    def __str__(self):
        return f"{self.resultado} - {self.reconocimiento}"


class EntradaSalida(models.Model):
    TIPOS = [("ENTRADA", "Entrada"), ("SALIDA", "Salida")]

    intento = models.ForeignKey(
        IntentoAcceso, on_delete=models.CASCADE, related_name="movimientos"
    )
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=TIPOS)

    class Meta:
        db_table = "entradas_salidas"

    def __str__(self):
        return f"{self.tipo} - {self.fecha} {self.hora}"
