from django.contrib import admin
from django.urls import path, include
from MiApp import views

from django.conf import settings
from django.conf.urls.static import static  # Import necesario para servir estáticos en desarrollo

urlpatterns = [
    path('admin/', admin.site.urls),
    path('miapp/', include('MiApp.urls')),
    path('', views.login_usuario, name='login'),
    path('recuperar/', views.recuperar_contraseña, name='recuperar'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('consultar-disponibilidad/', views.consultar_disponibilidad, name='consultar_disponibilidad'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
]

# Añadir manejo de archivos estáticos durante desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')


