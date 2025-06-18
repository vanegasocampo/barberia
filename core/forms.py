# core/forms.py

from django import forms
from .models import Barbero, Servicio

class BarberoForm(forms.ModelForm):
    class Meta:
        model = Barbero
        fields = ['nombre']

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'duracion', 'precio']