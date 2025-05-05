from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

from django.db import models

class Usuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
    ]

    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=128)
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES, default='cliente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Agregar los campos faltantes
    last_login = models.DateTimeField(auto_now=True, null=True, blank=True)  # Esto simula el campo last_login
    is_active = models.BooleanField(default=True)  # Esto simula el campo is_active

    def __str__(self):
        return f"{self.nombre} ({self.tipo_usuario})"


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    preferencias = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.usuario.nombre}"


class Notificacion(models.Model):
    id_notificacion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=50)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return f"Notificación a {self.usuario.nombre}"


class Habitacion(models.Model):
    ESTADO_CHOICES = [
        ('ocupada', 'Ocupada'),
        ('disponible', 'Disponible'),
    ]

    id_habitacion = models.AutoField(primary_key=True)
    numero = models.CharField(max_length=10)
    tipo = models.CharField(max_length=50)
    precio_noche = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)
    descripcion = models.TextField()

    def __str__(self):
        return f"Habitación {self.numero} - {self.estado}"


class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado_reserva = models.CharField(max_length=50)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reserva {self.id_reserva} de {self.usuario.nombre}"


class HistorialReserva(models.Model):
    id_historial = models.AutoField(primary_key=True)
    accion = models.CharField(max_length=100)
    fecha_accion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)

    def __str__(self):
        return f"Historial {self.id_historial} - {self.accion}"


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    estado_pago = models.CharField(max_length=50)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)

    def __str__(self):
        return f"Pago {self.id_pago} - {self.monto} CLP"


