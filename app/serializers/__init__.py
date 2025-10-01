from .auth import *
from .propiedad import *
from .residencia import *
from .residente import *
from .apartamento import *
from .visita import *
from .visitante import *
from .vehiculo import *
from .reserva import *
from .area_comun import *

from .detalle_reserva import *
from .avisos import AvisoSerializer, AvisoResidenteSerializer




__all__ = (
    'EmailOrUsernameTokenObtainPairSerializer',
    'UsuarioResidenteCreateSerializer',
    'PropiedadAsignarSerializer',
    'UsuarioPropietarioCreateSerializer',
    'PropiedadSerializer',
    'ResidenciaSerializer',
    'ResidenteSerializer',
    'ApartamentoSerializer',
    'PropietarioSerializer',
    'ResidenciaAsignarSerializer',
    'VehiculoSerializer',
    'VisitanteSerializer',
    'VisitaSerializer',
    'ReservaSerializer',
    'AreaComunSerializer',
    'DetalleReservaSerializer',
    'AvisoSerializer',
    'AvisoResidenteSerializer',
)
#Cambios aplicados#