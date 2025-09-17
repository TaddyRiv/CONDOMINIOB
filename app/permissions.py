from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "rol", None) == "ADMIN")

##
class IsAuthenticatedAndActive(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active)
class IsAdminOrEmpleado(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "rol", "").upper() in ["ADMIN", "EMPLEADO"]
class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "rol", "").upper() in ["ADMIN", "EMPLEADO"]:
            return True
        if hasattr(obj, "usuario_id"):  # Reserva
            return obj.usuario_id == request.user.id
        if hasattr(obj, "reserva"):  # DetalleReserva
            return obj.reserva.usuario_id == request.user.id
        return False

