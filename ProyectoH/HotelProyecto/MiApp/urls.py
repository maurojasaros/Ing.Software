from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('recuperar/', views.recuperar_contraseña, name='recuperar'),
    path('login/', views.login_usuario, name='login'),
    path('home/', views.home, name='home'),
    path('cerrar-sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('perfil/', views.perfil, name='perfil'),
    path('consultar-disponibilidad/', views.consultar_disponibilidad, name='consultar_disponibilidad'),
    path('habitaciones/', views.listar_habitaciones, name='listar_habitaciones'),
    path('habitacion/agregar/', views.agregar_habitacion, name='agregar_habitacion'),
    path('habitacion/editar/<int:id_habitacion>/', views.editar_habitacion, name='editar_habitacion'),
    path('habitacion/eliminar/<int:id_habitacion>/', views.eliminar_habitacion, name='eliminar_habitacion'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('usuarios/editar/<int:id_usuario>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:id_usuario>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('reservar/<int:id_habitacion>/', views.reservar, name='reservar'),
    path('confirmar-reserva/<int:id_habitacion>/', views.confirmar_reserva, name='confirmar_reserva'),
    path('historial_reservas_usuario/', views.historial_reservas_usuario, name='historial_reservas_usuario'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
    path('reservas/', views.listar_reservas, name='listar_reservas'),  # Página de reservas
    path('confirmar_anulacion/<int:id_reserva>/', views.confirmar_anulacion, name='confirmar_anulacion'),  # Anular reserva
    path('eliminar-reserva/<int:id_reserva>/', views.eliminar_reserva, name='eliminar_reserva'),
    path('mensajes/', views.listar_mensajes, name='listar_mensajes'),
    path('enviar-mensaje/<int:id_destinatario>/', views.enviar_mensaje, name='enviar_mensaje'),
    path('mensajes-admin/', views.listar_mensajes, name='mensajes_admin'),
    path('enviar-mensaje-admin/', views.enviar_mensaje, name='enviar_mensaje_admin'),
    path('iniciar-pago/', views.iniciar_pago, name='iniciar_pago'),
    path('respuesta-pago/', views.respuesta_pago, name='respuesta_pago'),
    path('retorno-pago/', views.retorno_pago, name='retorno_pago'),
    
    
    
    
]