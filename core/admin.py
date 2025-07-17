# from django.contrib import admin
# from .models import Barberia, Barbero, Servicio, Cita

# admin.site.register(Barberia)
# admin.site.register(Barbero)
# admin.site.register(Servicio)
# admin.site.register(Cita)


from django.contrib import admin
from .models import Barberia, Barbero, Servicio, Cita


@admin.register(Barberia)
class BarberiaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'direccion', 'dueño')
    search_fields = ('nombre', 'direccion', 'telefono', 'dueño__username')
    list_per_page = 20


@admin.register(Barbero)
class BarberoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'barberia')
    search_fields = ('nombre',)
    list_filter = ('barberia',)
    list_per_page = 20


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'duracion', 'barberia')
    search_fields = ('nombre',)
    list_filter = ('barberia',)
    list_per_page = 20


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('cliente_nombre', 'barbero', 'servicio', 'fecha_hora', 'confirmada')
    search_fields = ('cliente_nombre', 'cliente_telefono')
    list_filter = ('confirmada', 'barbero', 'servicio')
    date_hierarchy = 'fecha_hora'
    list_per_page = 20
