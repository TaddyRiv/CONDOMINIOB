from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from app.models.usuario import Usuario
from app.forms import UsuarioCreationForm, UsuarioChangeForm
from app.models import Apartamento, Residencia
from app.models import Reserva, DetalleReserva, AreaComun

# Inline para ver estancias (historial de ocupación) en el detalle del Usuario:

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Usa los formularios custom
    add_form = UsuarioCreationForm
    form = UsuarioChangeForm
    model = Usuario

    # Qué columnas ver en la lista
    list_display = ("email", "username", "first_name", "last_name", "ci", "rol", "is_staff", "is_active", "date_joined")
    list_filter = ("rol", "is_staff", "is_active")

    # Búsqueda
    search_fields = ("email", "username", "first_name", "last_name", "ci")
    ordering = ("email",)  # como tu login es por email, suele ser cómodo

    # Campos de solo lectura
    readonly_fields = ("last_login", "date_joined")

    # Secciones del formulario de edición (DETALLE)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Información personal", {"fields": ("first_name", "last_name", "email", "ci", "telefono", "foto", "fecha_nacimiento")}),
        ("Roles y permisos", {"fields": ("rol", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )

    # Secciones del formulario de creación (ALTA)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "username",
                "first_name", "last_name",
                "ci", "telefono", "fecha_nacimiento", "foto",
                "rol", "is_staff", "is_active",
                "password1", "password2",
            ),
        }),
    )

    readonly_fields = ("last_login", "date_joined")
 

@admin.register(Apartamento)
class ApartamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'estado')
    search_fields = ('numero',)

@admin.register(Residencia)
class ResidenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'apartamento', 'fecha_inicio', 'fecha_fin', 'created_at')
    list_filter = ('fecha_fin',)
    search_fields = ('usuario__email', 'apartamento__numero')
    




## MODELOS DE DETALLE RESERVA, AREA COMUN, RESERVA
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'area_comun', 'fecha', 'hora_inicio', 'hora_fin', 'estado', 'fecha_creacion')
    list_filter = ('estado',)
    search_fields = ('usuario__email', 'area_comun__nombre')
@admin.register(DetalleReserva)
class DetalleReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'reserva', 'descripcion')
    search_fields = ('reserva__usuario__email', 'reserva__area_comun__nombre')
@admin.register(AreaComun)
class AreaComunAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre') 
    list_filter = ('estado',)
    search_fields = ('nombre',)

    