from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters
from app.models.vehiculo import Vehiculo
from app.serializers.vehiculo import VehiculoSerializer

from app.models.acceso import PuntoAcceso, Camara, Reconocimiento, IntentoAcceso, EntradaSalida
from app.serializers.acceso import (
    PuntoAccesoSerializer, CamaraSerializer,
    ReconocimientoSerializer, IntentoAccesoSerializer,
    EntradaSalidaSerializer
)


# ---------- PUNTO DE ACCESO ----------
class PuntoAccesoViewSet(viewsets.ModelViewSet):
    queryset = PuntoAcceso.objects.all()
    serializer_class = PuntoAccesoSerializer


# ---------- CAMARA ----------
class CamaraViewSet(viewsets.ModelViewSet):
    queryset = Camara.objects.all()
    serializer_class = CamaraSerializer


# ---------- RECONOCIMIENTO ----------
class ReconocimientoViewSet(viewsets.ModelViewSet):
    queryset = Reconocimiento.objects.all()
    serializer_class = ReconocimientoSerializer

    @action(detail=False, methods=["post"])
    def procesar(self, request):
        """
        Procesa una imagen o un texto de placa.
        1. Si viene 'texto' en el body → se valida directo contra la BD.
        2. Si viene 'captura' (imagen) → se intenta leer la placa con EasyOCR.
        """
        texto = request.data.get("texto")
        imagen = request.FILES.get("captura")

        if not texto and not imagen:
            return Response(
                {"error": "Debes enviar 'texto' o 'captura'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Caso 1: ya se recibe el texto de placa ---
        if texto:
            placa_detectada = texto.strip().upper()

        # --- Caso 2: se recibe una imagen y se procesa con OCR ---
        elif imagen:
            # Guardar el reconocimiento en la BD
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            reconocimiento = serializer.save()

            # Procesar imagen con OpenCV + EasyOCR
            path = reconocimiento.captura.path
            frame = cv2.imread(path)
            results = reader.readtext(frame)

            placa_detectada = None
            for (bbox, text, prob) in results:
                if prob > 0.3:  # confianza mínima
                    placa_detectada = text.strip().upper()
                    break

            if not placa_detectada:
                intento = IntentoAcceso.objects.create(
                    reconocimiento=reconocimiento,
                    resultado="DENEGADO",
                    motivo="No se pudo leer la placa"
                )
                return Response({
                    "placa_detectada": None,
                    "resultado": intento.resultado,
                    "motivo": intento.motivo
                }, status=status.HTTP_200_OK)

        # --- Buscar vehículo en la BD ---
        vehiculo = Vehiculo.objects.filter(placa__iexact=placa_detectada).first()

        reconocimiento = Reconocimiento.objects.create(
            tipo="PLACA",
            captura=imagen if imagen else None
        )

        if vehiculo:
            intento = IntentoAcceso.objects.create(
                reconocimiento=reconocimiento,
                vehiculo=vehiculo,
                resultado="ACEPTADO",
                motivo="Vehículo registrado"
            )
        else:
            intento = IntentoAcceso.objects.create(
                reconocimiento=reconocimiento,
                resultado="DENEGADO",
                motivo="Vehículo no encontrado"
            )

        return Response({
            "placa_detectada": placa_detectada,
            "resultado": intento.resultado,
            "motivo": intento.motivo
        }, status=status.HTTP_201_CREATED)


# ---------- INTENTO DE ACCESO ----------
class IntentoAccesoViewSet(viewsets.ModelViewSet):
    queryset = IntentoAcceso.objects.all()
    serializer_class = IntentoAccesoSerializer


# ---------- ENTRADA / SALIDA ----------
class EntradaSalidaViewSet(viewsets.ModelViewSet):
    queryset = EntradaSalida.objects.all()
    serializer_class = EntradaSalidaSerializer

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["placa"]