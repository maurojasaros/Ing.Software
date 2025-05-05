from django.contrib import admin
from .models import Usuario, Habitacion
# Register your models here.

# Registrar el modelo Usuario en el panel de administración
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'tipo_usuario', 'fecha_creacion', 'last_login', 'is_active')
    search_fields = ('nombre', 'correo')  # Campos para búsqueda
    list_filter = ('tipo_usuario', 'is_active')  # Filtros disponibles

# Registrar el modelo Habitacion en el panel de administración
@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo', 'precio_noche', 'estado', 'descripcion')
    search_fields = ('numero', 'tipo')  # Campos para búsqueda
    list_filter = ('estado',)
