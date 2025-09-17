# app/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from app.views.auth import EmailOrUsernameTokenObtainPairView
from app.views.residencia import ResidenciaViewSet
from app.views.apartamento import ApartamentoViewSet
from app.views.residente import ResidenteAltaViewSet
from app.views.residencia_asignar import ResidenciaAsignacionViewSet
from app.views.residente_usuario import ResidenteUsuarioViewSet
from app.views.propietario_usuario import PropietarioUsuarioViewSet
from app.views.propiedad_asignar import PropiedadAsignacionViewSet
from app.views.propietario_usuario import PropietarioListView, PropietarioDetailUpdateView
from app.views.apartamento import ApartamentoListView
from app.views.residente_usuario import ResidenteListView
from app.views.servicio import ServicioViewSet
from app.views.cargo import CargoViewSet
from app.views.pago import PagoViewSet

from app.views.reserva import ReservaViewSet
from app.views.area_comun import AreaComunViewSet
from app.views.detalle_reserva import DetalleReservaViewSet


urlpatterns = [

    path("auth/login/", EmailOrUsernameTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("residencias/", ResidenciaViewSet.as_view({'get': 'list', 'post': 'create'}), name="residencia-list"),
    path("apartamentos/", ApartamentoViewSet.as_view({'get': 'list', 'post': 'create'}), name="apartamento-list"),
    path("residentes/", ResidenteAltaViewSet.as_view({'post': 'create'}), name="residente-create"),
    path("residencias/asignar/", ResidenciaAsignacionViewSet.as_view({'post': 'create'}), name="residencia-asignar"),
    path("usuarios-residentes/", ResidenteUsuarioViewSet.as_view({'post': 'create'}), name="usuario-residente-create"),
    path("usuarios-propietarios/", PropietarioUsuarioViewSet.as_view({'post': 'create'}), name="usuario-propietario-create"),
    path("propiedades/asignar/", PropiedadAsignacionViewSet.as_view({'post': 'create'}), name="propiedad-asignar"),
    path("propietarios/", PropietarioListView.as_view(), name="propietario-list"),
    path("propietarios/<int:pk>/", PropietarioDetailUpdateView.as_view(), name="propietario-detail-update"),
    path("apartamentos/list/", ApartamentoListView.as_view(), name="apartamento-list-view"),
    path("residentes/list/", ResidenteListView.as_view(), name="residente-list-view"),
    path("servicios/", ServicioViewSet.as_view({'get': 'list', 'post': 'create'}), name="servicio-list"),
    path("cargos/", CargoViewSet.as_view({'get': 'list', 'post': 'create'}), name="cargo-list"),
    path("pagos/", PagoViewSet.as_view({'get': 'list', 'post': 'create'}), name="pago-list"),
    
    path("reservas/", ReservaViewSet.as_view({'get': 'list', 'post': 'create'}), name="reserva-list"),
    path("areas-comunes/", AreaComunViewSet.as_view({'get': 'list', 'post': 'create'}), name="areacomun-list"),
    path("detalles-reserva/", DetalleReservaViewSet.as_view({'get': 'list', 'post': 'create'}), name="detalle-reserva-list"),

    

]
