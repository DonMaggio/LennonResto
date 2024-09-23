from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 4:
            raise forms.ValidationError("El nombre de usuario debe tener al menos 4 caracteres.")
        if not username.isalnum():
            raise forms.ValidationError("El nombre de usuario solo puede contener letras y números.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este usuario ya está registrado.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.get('email')
        if commit:
            user.save()
        return user