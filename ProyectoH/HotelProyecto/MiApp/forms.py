from django import forms
from .models import Usuario, Habitacion  # ✅ solo esta importación está bien

class RegistroForm(forms.ModelForm):
    contraseña = forms.CharField(widget=forms.PasswordInput())
    confirmar_contraseña = forms.CharField(widget=forms.PasswordInput(), label="Confirmar Contraseña")

    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'contraseña']

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Usuario.objects.filter(correo=correo).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return correo

    def clean(self):
        cleaned_data = super().clean()
        contraseña = cleaned_data.get("contraseña")
        confirmar_contraseña = cleaned_data.get("confirmar_contraseña")

        if contraseña and confirmar_contraseña and contraseña != confirmar_contraseña:
            self.add_error('confirmar_contraseña', "Las contraseñas no coinciden.")

        # Asignar 'cliente' a tipo_usuario automáticamente
        cleaned_data['tipo_usuario'] = 'cliente'  # Esto garantiza que el tipo de usuario sea siempre 'cliente'
        return cleaned_data



class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitacion
        fields = ['numero', 'tipo', 'precio_noche', 'estado', 'descripcion']

from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'contraseña', 'tipo_usuario', 'is_active']  # Definir los campos que estarán en el formulario

    # Campo contraseña, es recomendable usar el widget PasswordInput para que sea más seguro
    contraseña = forms.CharField(widget=forms.PasswordInput())

    # Validación de email (por si necesitas alguna lógica adicional)
    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        # Aquí puedes agregar lógica para validar el correo si es necesario
        return correo

