from django.contrib import admin
from .models import Barberia, Barbero, Servicio, Cita

admin.site.register(Barberia)
admin.site.register(Barbero)
admin.site.register(Servicio)
admin.site.register(Cita)
