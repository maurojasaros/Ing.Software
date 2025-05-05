import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password, check_password
from .models import Usuario, PerfilUsuario, Habitacion, Reserva, HistorialReserva, Notificacion
from .forms import RegistroForm, HabitacionForm
from datetime import datetime
from django.utils import timezone
from datetime import datetime
from dateutil.parser import parse as parse_date


# Configuración básica de logging
logger = logging.getLogger(__name__)

# Vista de login
def login_usuario(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contraseña = request.POST.get('contraseña')

        logger.debug(f"Intentando login con correo: {correo}")

        usuario = Usuario.objects.filter(correo=correo).first()

        if usuario:
            logger.debug(f"Usuario encontrado: {usuario.nombre} (ID: {usuario.id_usuario})")

            if check_password(contraseña, usuario.contraseña):
                logger.debug(f"Contraseña correcta para el usuario: {usuario.nombre}")
                request.session['usuario_id'] = usuario.id_usuario
                login(request, usuario)
                return redirect('home')
            else:
                logger.warning(f"Contraseña incorrecta para el usuario: {usuario.nombre}")
                messages.error(request, 'Contraseña incorrecta.')
        else:
            logger.warning(f"El usuario con correo {correo} no existe.")
            messages.error(request, 'El usuario no existe.')

    return render(request, 'login.html')

# Vista de registro
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.contraseña = make_password(form.cleaned_data['contraseña'])
            usuario.save()
            return redirect('home')
    else:
        form = RegistroForm()
    
    return render(request, 'registro.html', {'form': form})

# Vista protegida
def vista_protegida(request):
    if request.session.get('usuario_id'):
        return HttpResponse("Esta es una vista protegida")
    else:
        return redirect('login')

# Cerrar sesión
def cerrar_sesion(request):
    logout(request)
    return redirect('login')

# Recuperar contraseña
def recuperar_contraseña(request):
    return render(request, 'recuperar.html')

# Vista home
def home(request):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)
            return render(request, 'home.html', {'usuario': usuario})
        except Usuario.DoesNotExist:
            pass
    return redirect('login')

# Vista perfil
def perfil(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
    except Usuario.DoesNotExist:
        return redirect('login')

    perfil, creado = PerfilUsuario.objects.get_or_create(usuario=usuario)

    old_nombre = usuario.nombre
    old_correo = usuario.correo
    old_telefono = perfil.telefono
    old_direccion = perfil.direccion
    old_preferencias = perfil.preferencias

    if request.method == 'POST':
        usuario.nombre = request.POST.get('nombre')
        usuario.correo = request.POST.get('correo')
        usuario.save()

        perfil.telefono = request.POST.get('telefono')
        perfil.direccion = request.POST.get('direccion')
        perfil.preferencias = request.POST.get('preferencias')
        perfil.save()

        if (usuario.nombre != old_nombre or usuario.correo != old_correo or
            perfil.telefono != old_telefono or perfil.direccion != old_direccion or
            perfil.preferencias != old_preferencias):
            messages.success(request, '¡Perfil actualizado con éxito!')

        return redirect('home')

    contexto = {
        'usuario': usuario,
        'perfil': perfil
    }
    return render(request, 'perfil.html', contexto)

# Consultar disponibilidad de habitaciones
def consultar_disponibilidad(request):
    if request.method == 'GET':
        fecha_entrada = request.GET.get('fecha-entrada')
        fecha_salida = request.GET.get('fecha-salida')

        if fecha_entrada and fecha_salida:
            try:
                habitaciones_disponibles = Habitacion.objects.filter(estado='disponible')
                if habitaciones_disponibles:
                    contexto = {
                        'habitaciones_disponibles': habitaciones_disponibles,
                        'fecha_entrada': fecha_entrada,
                        'fecha_salida': fecha_salida
                    }
                else:
                    messages.error(request, 'No hay habitaciones disponibles para esas fechas.')
                    contexto = {}
            except Exception as e:
                messages.error(request, f'Ocurrió un error al consultar la disponibilidad: {str(e)}')
                contexto = {}
            return render(request, 'consultar.html', contexto)

    return render(request, 'consultar.html')

# Listar habitaciones (solo admin)
def listar_habitaciones(request):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        if usuario.tipo_usuario == 'admin':
            habitaciones = Habitacion.objects.all()
            return render(request, 'listar_habitaciones.html', {'habitaciones': habitaciones})
        else:
            return redirect('home')
    return redirect('login')

# Agregar habitación (solo admin)
def agregar_habitacion(request):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        if usuario.tipo_usuario == 'admin':
            if request.method == 'POST':
                form = HabitacionForm(request.POST)
                if form.is_valid():
                    form.save()
                    return redirect('listar_habitaciones')
            else:
                form = HabitacionForm()
            return render(request, 'agregar_habitacion.html', {'form': form})
        else:
            return redirect('home')
    return redirect('login')

# Editar habitación (solo admin)
def editar_habitacion(request, id_habitacion):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        if usuario.tipo_usuario == 'admin':
            habitacion = Habitacion.objects.get(id_habitacion=id_habitacion)
            if request.method == 'POST':
                form = HabitacionForm(request.POST, instance=habitacion)
                if form.is_valid():
                    form.save()
                    return redirect('listar_habitaciones')
            else:
                form = HabitacionForm(instance=habitacion)
            return render(request, 'editar_habitacion.html', {'form': form})
        else:
            return redirect('home')
    return redirect('login')

# Eliminar habitación (solo admin)
def eliminar_habitacion(request, id_habitacion):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        if usuario.tipo_usuario == 'admin':
            habitacion = Habitacion.objects.get(id_habitacion=id_habitacion)
            if request.method == 'POST':
                habitacion.delete()
                return redirect('listar_habitaciones')
            return render(request, 'eliminar_habitacion.html', {'habitacion': habitacion})
        else:
            return redirect('home')
    return redirect('login')


def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'listar_usuarios.html', {'usuarios': usuarios})

from django.shortcuts import render, redirect
from .forms import UsuarioForm  # Asegúrate de crear este formulario

def agregar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.contraseña = make_password(form.cleaned_data['contraseña'])
            usuario.save()
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'agregar_usuario.html', {'form': form})

def editar_usuario(request, id_usuario):
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            nueva_contraseña = form.cleaned_data['contraseña']

            # Si cambió la contraseña, la hasheamos
            if not nueva_contraseña.startswith('pbkdf2_'):
                usuario.contraseña = make_password(nueva_contraseña)

            usuario.save()
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'editar_usuario.html', {'form': form})


def eliminar_usuario(request, id_usuario):
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    if request.method == 'POST':
        usuario.delete()
        return redirect('listar_usuarios')
    return render(request, 'confirmar_eliminacion_usuario.html', {'usuario': usuario})


def reservar(request, id_habitacion):
    habitacion = get_object_or_404(Habitacion, id_habitacion=id_habitacion)
    fecha_entrada = request.GET.get('fecha_entrada')
    fecha_salida = request.GET.get('fecha_salida')

    if fecha_entrada and fecha_salida:
        entrada = datetime.strptime(fecha_entrada, '%Y-%m-%d').date()
        salida = datetime.strptime(fecha_salida, '%Y-%m-%d').date()
        dias = (salida - entrada).days
        total = dias * habitacion.precio_noche
    else:
        entrada = salida = dias = total = None

    return render(request, 'reservar.html', {
        'habitacion': habitacion,
        'fecha_entrada': entrada,
        'fecha_salida': salida,
        'dias': dias,
        'total': total
    })


def historial_reservas_usuario(request):
    if not request.session.get("usuario_id"):
        return redirect("login")

    try:
        usuario = Usuario.objects.get(id_usuario=request.session["usuario_id"])
    except Usuario.DoesNotExist:
        return HttpResponse("Usuario no válido. Por favor inicia sesión.", status=400)

    historial = HistorialReserva.objects.filter(usuario=usuario).select_related('reserva', 'reserva__habitacion').order_by('-fecha_accion')

    return render(request, 'historial_reservas_usuario.html', {'historial': historial, 'usuario': usuario})

from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuario, Habitacion, Reserva, HistorialReserva

def confirmar_reserva(request, id_habitacion):
    if not request.session.get("usuario_id"):
        return redirect("login")

    try:
        usuario = Usuario.objects.get(id_usuario=request.session["usuario_id"])
    except Usuario.DoesNotExist:
        return HttpResponse("Usuario no válido. Por favor inicia sesión.", status=400)

    habitacion = get_object_or_404(Habitacion, id_habitacion=id_habitacion)

    fecha_entrada = request.POST.get('fecha_entrada')
    fecha_salida = request.POST.get('fecha_salida')

    try:
        fecha_inicio = datetime.strptime(fecha_entrada, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_salida, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("Error al procesar las fechas. Usa el formato YYYY-MM-DD.", status=400)

    if fecha_inicio >= fecha_fin:
        return HttpResponse("La fecha de entrada debe ser anterior a la fecha de salida.", status=400)

    reservas_existentes = Reserva.objects.filter(
        habitacion=habitacion,
        fecha_inicio__lt=fecha_fin,
        fecha_fin__gt=fecha_inicio,
        estado_reserva='confirmada'
    )

    if reservas_existentes.exists():
        return render(request, 'confirmar_reserva.html', {
            'error': "La habitación ya está reservada para las fechas seleccionadas.",
            'habitacion': habitacion,
            'fecha_entrada': fecha_entrada,
            'fecha_salida': fecha_salida
        })

    # Crear reserva
    nueva_reserva = Reserva.objects.create(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado_reserva='confirmada',
        usuario=usuario,
        habitacion=habitacion
    )

    # Crear historial
    HistorialReserva.objects.create(
        accion=f"Reserva confirmada para la habitación {habitacion.numero}",
        usuario=usuario,
        reserva=nueva_reserva
    )

    # ✅ Crear notificación para el usuario
    notificacion = Notificacion.objects.create(
        usuario=usuario,
        mensaje=f"Tu reserva para la habitación {habitacion.numero} ha sido confirmada del {fecha_inicio} al {fecha_fin}.",
        tipo="reserva",
        estado="no leída"
    )

    # Imprimir para verificar si la notificación se está creando correctamente
    print(f"Notificación creada: {notificacion.mensaje}")

    cantidad_noches = (fecha_fin - fecha_inicio).days
    total_pago = cantidad_noches * habitacion.precio_noche

    fecha_inicio_formateada = fecha_inicio.strftime('%Y-%m-%d')
    fecha_fin_formateada = fecha_fin.strftime('%Y-%m-%d')

    return render(request, 'confirmar_reserva.html', {
        'reserva': nueva_reserva,
        'habitacion': habitacion,
        'fecha_entrada': fecha_inicio_formateada,
        'fecha_salida': fecha_fin_formateada,
        'total_pago': total_pago
    })



def notificaciones(request):
    if not request.session.get("usuario_id"):
        return redirect("login")

    try:
        usuario = Usuario.objects.get(id_usuario=request.session["usuario_id"])
    except Usuario.DoesNotExist:
        return HttpResponse("Usuario no válido. Por favor inicia sesión.", status=400)

    # Obtener todas las notificaciones no leídas del usuario
    notificaciones = Notificacion.objects.filter(usuario=usuario)

    # Verificar si realmente hay notificaciones
    print(f"Notificaciones encontradas: {notificaciones.count()}")  # Verifica cuántas notificaciones se encuentran

    # Marcar las notificaciones como leídas
    notificaciones.update(estado="leída")

    return render(request, 'notificaciones.html', {'notificaciones': notificaciones})


from django.views.decorators.csrf import csrf_exempt
# Vista para ver las reservas y anularlas
def listar_reservas(request):
    if not request.session.get("usuario_id"):
        return redirect("login")

    try:
        usuario = Usuario.objects.get(id_usuario=request.session["usuario_id"])
    except Usuario.DoesNotExist:
        return HttpResponse("Usuario no válido. Por favor inicia sesión.", status=400)

    if usuario.tipo_usuario == 'admin':
        reservas = Reserva.objects.select_related('habitacion', 'usuario').all()
    else:
        reservas = Reserva.objects.select_related('habitacion').filter(usuario=usuario)

    return render(request, 'reservas.html', {'usuario': usuario, 'reservas': reservas})



# Vista para anular una reserva específica
def confirmar_anulacion(request, id_reserva):
    if not request.session.get("usuario_id"):
        return redirect("login")

    try:
        usuario = Usuario.objects.get(id_usuario=request.session["usuario_id"])
    except Usuario.DoesNotExist:
        return HttpResponse("Usuario no válido. Por favor inicia sesión.", status=400)

    # Obtener la reserva por id
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)

    # Comprobar si el usuario tiene permiso para anular (dueño o admin)
    if reserva.usuario != usuario and usuario.tipo_usuario != 'admin':
        return HttpResponse("No puedes anular esta reserva.", status=403)

    # Cambiar el estado de la reserva a 'anulada'
    reserva.estado_reserva = 'anulada'
    reserva.save()

    # Crear historial de la anulación
    HistorialReserva.objects.create(
        accion=f"Reserva anulada para la habitación {reserva.habitacion.numero}",
        usuario=usuario,
        reserva=reserva
    )

    # Crear notificación para el usuario dueño de la reserva
    Notificacion.objects.create(
        usuario=reserva.usuario,  # notifica al dueño de la reserva
        mensaje=f"Tu reserva para la habitación {reserva.habitacion.numero} ha sido anulada.",
        tipo="anulación",
        estado="no leída"
    )

    return redirect('listar_reservas')




def eliminar_reserva(request, id_reserva):
    if not request.session.get("usuario_id"):
        return redirect("login")

    try:
        usuario = Usuario.objects.get(id_usuario=request.session["usuario_id"])
    except Usuario.DoesNotExist:
        return HttpResponse("Usuario no válido.", status=400)

    if usuario.tipo_usuario != 'admin':
        return HttpResponse("Acceso no autorizado.", status=403)

    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)
    reserva.delete()

    return redirect('listar_reservas')



def enviar_mensaje(request, id_destinatario=None):
    if not request.session.get("usuario_id"):
        return redirect("login")

    usuario_origen = Usuario.objects.get(id_usuario=request.session["usuario_id"])

    if request.method == "POST":
        mensaje = request.POST.get("mensaje")
        if id_destinatario:
            usuario_destino = get_object_or_404(Usuario, id_usuario=id_destinatario)
        else:
            id_destinatario = request.POST.get("id_destinatario")
            usuario_destino = get_object_or_404(Usuario, id_usuario=id_destinatario)

        Notificacion.objects.create(
            usuario=usuario_destino,
            mensaje=f"Mensaje de {usuario_origen.nombre}: {mensaje}",
            tipo="mensaje",
            estado="no leído"
        )

        messages.success(request, "✅ Mensaje enviado correctamente.")
        return redirect("home")  # O cualquier vista que desees redirigir después

    if usuario_origen.tipo_usuario == "admin":
        # Si el usuario es un admin, muestra la lista de usuarios (clientes) para que seleccione uno
        usuarios = Usuario.objects.filter(tipo_usuario='cliente')
        return render(request, "enviar_mensaje_admin.html", {"usuarios": usuarios})

    # Si es un cliente, simplemente mostrar el destinatario especificado
    destinatario = get_object_or_404(Usuario, id_usuario=id_destinatario)
    return render(request, "enviar_mensaje.html", {"destinatario": destinatario})























def listar_mensajes(request):
    if not request.session.get("usuario_id"):
        return redirect("login")

    usuario = Usuario.objects.get(id_usuario=request.session["usuario_id"])
    mensajes = Notificacion.objects.filter(usuario=usuario, tipo="mensaje").order_by("-fecha_envio")

    return render(request, "mensajes.html", {"mensajes": mensajes, "usuario": usuario})


def ver_mensajes_admin(request):
    if not request.session.get("usuario_id"):
        return redirect("login")

    # Solo los administradores pueden ver esta página
    usuario = Usuario.objects.get(id_usuario=request.session["usuario_id"])

    if usuario.tipo_usuario != 'admin':
        return redirect("home")  # Si no es admin, lo redirigimos al home

    # Obtener todas las notificaciones de tipo "mensaje" para el admin (de los clientes)
    mensajes = Notificacion.objects.filter(tipo="mensaje").order_by("-fecha_envio")

    # Si deseas marcar los mensajes como leídos en la base de datos:
    for mensaje in mensajes:
        if mensaje.estado == "no leído":
            mensaje.estado = "leído"
            mensaje.save()  # Guardamos el cambio en la base de datos

    return render(request, "mensajes_admin.html", {"mensajes": mensajes, "usuario": usuario})

