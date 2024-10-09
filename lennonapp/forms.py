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
            raise forms.ValidationError("The email address is already registered.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 4:
            raise forms.ValidationError("The username must be at least 4 characters long.")
        if not username.isalnum():
            raise forms.ValidationError("The username can only contain letters and numbers.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This user is already registered.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        #user.email = self.get('email')
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user