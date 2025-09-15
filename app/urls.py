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

]
