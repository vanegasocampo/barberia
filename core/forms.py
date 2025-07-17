# core/forms.py

from django import forms
from .models import Barbero, Servicio

class BarberoForm(forms.ModelForm):
    class Meta:
        model = Barbero
        fields = ['nombre','telefono', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control rounded-pill'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control rounded-pill'}),
            'email': forms.EmailInput(attrs={'class': 'form-control rounded-pill'}),
        }

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'duracion', 'precio']