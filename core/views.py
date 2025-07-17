from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, TemplateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Barbero, Servicio, Cita

from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import BarberoForm , ServicioForm
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime , timedelta, time as dtime
from twilio.twiml.messaging_response import MessagingResponse
from django.utils import timezone
from django.utils.timezone import localtime, make_aware, now
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST


# --- AUTENTICACIÓN Y VISTAS GENERALES ---
class LoginView(DjangoLoginView):
    template_name = 'login.html' # Vista de login con plantilla personalizada

def logout_view(request):
    logout(request) # Cierra la sesión del usuario
    return redirect('login') # Redirige al login

@login_required
def home(request):
    return render(request, 'home.html') # Página principal tras iniciar sesión

# --- VISTAS DE BARBEROS ---
@method_decorator(login_required, name='dispatch')
class BarberoListView(ListView):
    model = Barbero
    template_name = 'barberos/lista.html'
    context_object_name = 'barberos'

    def get_queryset(self):
        return Barbero.objects.filter(barberia=self.request.user.barberia) # Filtra por barbería del usuario

    

class BarberoCreateView(LoginRequiredMixin, CreateView):
    model = Barbero
    form_class = BarberoForm
    template_name = 'barberos/formulario.html'
    success_url = reverse_lazy('barbero_list')

    def form_valid(self, form):
        try:
            form.instance.barberia = self.request.user.barberia # Asocia barbero a la barbería del usuario
        except ObjectDoesNotExist:
            messages.error(self.request, "Debes tener una barbería registrada antes de agregar barberos.")
            return redirect('barbero_list')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class BarberoUpdateView(LoginRequiredMixin, UpdateView):
    model = Barbero
    form_class = BarberoForm
    template_name = 'barberos/formulario.html'
    success_url = reverse_lazy('barbero_list')

@method_decorator(login_required, name='dispatch')
class BarberoDeleteView(LoginRequiredMixin, DeleteView):
    model = Barbero
    template_name = 'barberos/confirm_delete.html'
    success_url = reverse_lazy('barbero_list')


# --- VISTAS DE SERVICIOS ---
@method_decorator(login_required, name='dispatch')
class ServicioListView(ListView):
    model = Servicio
    template_name = 'servicios/lista.html'

@method_decorator(login_required, name='dispatch')
class ServicioCreateView(CreateView):
    model = Servicio
    form_class = ServicioForm
    template_name = 'servicios/formulario.html'
    success_url = reverse_lazy('servicio_list')

    def form_valid(self, form):
        form.instance.barberia = self.request.user.barberia # Asigna la barbería
        return super().form_valid(form)
    
class ServicioUpdateView(LoginRequiredMixin, UpdateView):
    model = Servicio
    form_class = ServicioForm
    template_name = 'servicios/formulario.html'
    success_url = reverse_lazy('servicio_list')

class ServicioDeleteView(LoginRequiredMixin, DeleteView):
    model = Servicio
    template_name = 'servicios/confirm_delete.html'
    success_url = reverse_lazy('servicio_list')


# --- VISTA DE AGENDA CON FILTRO POR BARBERO ---
@method_decorator(login_required, name='dispatch')
class AgendaView(TemplateView):
    template_name = 'agenda.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barberia = self.request.user.barberia
        barbero_id = self.request.GET.get('barbero')  # Obtener filtro por barbero

        # Lista de barberos de esta barbería para el formulario de filtro
        context['barberos'] = Barbero.objects.filter(barberia=barberia)

        # Si hay filtro por barbero, se usa, si no, se muestran todas las citas de la barbería
        if barbero_id:
            context['citas'] = Cita.objects.filter(barbero__barberia=barberia, barbero_id=barbero_id).order_by('fecha_hora')
            context['barbero_filtrado'] = int(barbero_id)
        else:
            context['citas'] = Cita.objects.filter(barbero__barberia=barberia).order_by('fecha_hora')


        return context


class BarberoCreateView(LoginRequiredMixin, CreateView):
    model = Barbero
    form_class = BarberoForm
    template_name = 'barberos/formulario.html'
    success_url = reverse_lazy('barbero_list')

    def form_valid(self, form):
        try:
            form.instance.barberia = self.request.user.barberia
        except ObjectDoesNotExist:
            messages.error(self.request, "Debes tener una barbería registrada antes de agregar barberos.")
            return redirect('barbero_list')
        return super().form_valid(form)


# --- WEBHOOK DE WHATSAPP CON TWILIO ---
user_states = {} # Estado por usuario

DIAS_SEMANA_ES = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "POST":
        data = request.POST
        mensaje = data.get('Body', '').strip()
        telefono = data.get('From', '').split(':')[-1]
        respuesta = ""

        estado = user_states.get(telefono, {}).get('estado', 'inicio')

        if estado == 'inicio':
            if mensaje.lower() in ['hola', 'hi', 'sí', 'si']:
                respuesta = "¡Hola! ¿Cuál es tu nombre para la cita?"
                user_states[telefono] = {'estado': 'esperando_nombre'}
            else:
                respuesta = "Bienvenido. Escribe *Hola* para comenzar a agendar tu cita."

        elif estado == 'esperando_nombre':
            user_states[telefono]['nombre'] = mensaje
            user_states[telefono]['estado'] = 'esperando_servicio'
            servicios = Servicio.objects.all()
            opciones = "\n".join([f"{s.id}. {s.nombre}" for s in servicios])
            respuesta = f"Hola {mensaje}, elige un servicio:\n{opciones}"

        elif estado == 'esperando_servicio':
            try:
                servicio_id = int(mensaje)
                servicio = Servicio.objects.get(id=servicio_id)
                user_states[telefono]['servicio'] = servicio
                user_states[telefono]['estado'] = 'esperando_barbero'

                barberos = Barbero.objects.filter(barberia=servicio.barberia)
                opciones = "\n".join([f"{b.id}. {b.nombre}" for b in barberos])
                respuesta = f"Perfecto. Elige un barbero:\n{opciones}"
            except:
                respuesta = "Servicio no válido. Por favor, responde con el número del servicio."



        elif estado == 'esperando_barbero':
            try:
                barbero_id = int(mensaje)
                barbero = Barbero.objects.get(id=barbero_id)
                user_states[telefono]['barbero'] = barbero
                user_states[telefono]['estado'] = 'seleccionando_dia'

                hoy = datetime.now().date()
                dias_disponibles = [(hoy + timedelta(days=i)) for i in range(7)]
                user_states[telefono]['opciones_dias'] = dias_disponibles

                opciones_str = "\n".join([
                    f"{i+1}. {DIAS_SEMANA_ES[d.strftime('%A')]} {d.strftime('%d-%m-%Y')}" for i, d in enumerate(dias_disponibles)
                ])
                respuesta = f"📅 Elige un día para tu cita:\n{opciones_str}\n\nResponde con el número del día."
            except:
                respuesta = "Barbero no válido. Por favor, responde con el número."

        elif estado == 'seleccionando_dia':
            try:
                opcion = int(mensaje) - 1
                fecha_dia = user_states[telefono]['opciones_dias'][opcion]
                barbero = user_states[telefono]['barbero']

                # Buscar horas disponibles de 9 a 17 (bloques de 1 hora)
                horas = []
                for h in range(9, 21):
                    posible = make_aware(datetime.combine(fecha_dia, dtime(h, 0)))
                    if not Cita.objects.filter(barbero=barbero, fecha_hora=posible).exists() and posible > now():
                        horas.append(posible)

                if not horas:
                    respuesta = "⚠️ No hay horas disponibles ese día. Elige otro día, por favor."
                else:
                    user_states[telefono]['opciones_horas'] = horas
                    user_states[telefono]['estado'] = 'seleccionando_hora'
                    opciones_str = "\n".join([f"{i+1}. {h.strftime('%H:%M')}" for i, h in enumerate(horas)])
                    respuesta = f"🕒 Estas son las horas disponibles para el {DIAS_SEMANA_ES[fecha_dia.strftime('%A')]} {fecha_dia.strftime('%d-%m-%Y')}:\n{opciones_str}\n\nEscribe el número de tu elección."
            except:
                respuesta = "Opción no válida. Por favor elige un número del día."

        elif estado == 'seleccionando_hora':
            try:
                opcion = int(mensaje) - 1
                fecha_hora = user_states[telefono]['opciones_horas'][opcion]

                datos = user_states[telefono]
                Cita.objects.create(
                    barbero=datos['barbero'],
                    servicio=datos['servicio'],
                    cliente_nombre=datos['nombre'],
                    cliente_telefono=telefono,
                    fecha_hora=fecha_hora,
                    confirmada=True
                )
                respuesta = f"✅ Cita registrada para {datos['nombre']} el {fecha_hora.strftime('%A %d-%m-%Y %H:%M')} con {datos['barbero'].nombre}."
                user_states.pop(telefono, None)
            except:
                respuesta = "Opción inválida. Por favor elige un número válido de la lista de horas."


        twilio_response = MessagingResponse()
        twilio_response.message(respuesta)
        return HttpResponse(str(twilio_response), content_type='application/xml')


# --- CALENDARIO VISUAL CON EVENTOS DINÁMICOS ---
@method_decorator(login_required, name='dispatch')
class CalendarioView(TemplateView):
    template_name = 'calendario.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barberia = self.request.user.barberia
        context['barberos'] = Barbero.objects.filter(barberia=barberia)

        barbero_id = self.request.GET.get('barbero')
        if barbero_id:
            context['barbero_filtrado'] = int(barbero_id)

        return context
    

@login_required
def citas_json(request):
    barberia = request.user.barberia
    barbero_id = request.GET.get('barbero')

    # Rango solicitado por FullCalendar
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')

    if not start_str or not end_str:
        return JsonResponse({"error": "Parámetros de fecha requeridos"}, status=400)

    start_date = datetime.fromisoformat(start_str).date()
    end_date = datetime.fromisoformat(end_str).date()

    citas = Cita.objects.filter(
        barbero__barberia=barberia,
        fecha_hora__date__range=(start_date, end_date)
    )

    if barbero_id:
        citas = citas.filter(barbero_id=barbero_id)

    eventos = []
    duracion_min = 60  # AHORA bloques de 1 HORA

    # Horario semanal
    horario_semanal = {
        0: (dtime(9, 0), dtime(21, 0)),  # Lunes
        1: (dtime(9, 0), dtime(21, 0)),
        2: (dtime(9, 0), dtime(21, 0)),
        3: (dtime(9, 0), dtime(21, 0)),
        4: (dtime(9, 0), dtime(21, 0)),
        5: (dtime(9, 0), dtime(21, 0)),
        6: (dtime(10, 0), dtime(18, 0)),  # Domingo
    }

    dia_actual = start_date
    while dia_actual <= end_date:
        dia_sem = dia_actual.weekday()
        inicio_dia, fin_dia = horario_semanal.get(dia_sem, (None, None))
        if not inicio_dia:
            dia_actual += timedelta(days=1)
            continue

        start_datetime = make_aware(datetime.combine(dia_actual, inicio_dia))
        end_datetime = make_aware(datetime.combine(dia_actual, fin_dia))

        citas_dia = citas.filter(fecha_hora__date=dia_actual)
        ocupados = [
            (localtime(c.fecha_hora), localtime(c.fecha_hora + c.servicio.duracion))
            for c in citas_dia
        ]
          
        # Crear un set de bloques ocupados redondeando fecha_hora al inicio de cada bloque
        horarios_ocupados = set(
            datetime.combine(c.fecha_hora.date(), dtime(c.fecha_hora.hour, 0)).replace(tzinfo=c.fecha_hora.tzinfo)
            for c in citas_dia
            )
        
        bloque = start_datetime

        while bloque < end_datetime:
            bloque_fin = bloque + timedelta(minutes=duracion_min)

            if bloque not in horarios_ocupados:
                disponible = all(bloque_fin <= i[0] or bloque >= i[1] for i in ocupados)

                if disponible:
                    eventos.append({
                    "title": f"{bloque.strftime('%H:%M')} - {bloque_fin.strftime('%H:%M')}\nDisponible",
                    "start": bloque.isoformat(),
                    "end": bloque_fin.isoformat(),
                    "color": "#d0ebff",  # Azul claro (más suave que el anterior)
                    "textColor": "#000711",
                })

            bloque += timedelta(minutes=duracion_min)
        dia_actual += timedelta(days=1)  # 👈 esto sigue abajo

    # Citas reales con color más visible
    for cita in citas:
        eventos.append({
            "id": cita.id, # 👈 necesario para cancelar
            "title": f"{cita.cliente_nombre} {cita.servicio.nombre} {cita.barbero.nombre}",
            "start": localtime(cita.fecha_hora).isoformat(),
            "end": (localtime(cita.fecha_hora) + cita.servicio.duracion).isoformat(),
            "color": "#01050a",  # Azul vivo para contraste
            "textColor": "#ffffff",  # Texto blanco para mayor legibilidad
             "estado": "agendada"  # 👈 clave para eventClick
            # "display": "block",
            # "description": f"{cita.cliente_nombre} - {cita.servicio.nombre}"
        })

    return JsonResponse(eventos, safe=False)


@login_required
@require_POST
def cancelar_cita(request):
    cita_id = request.POST.get('id')

    try:
        cita = Cita.objects.get(id=cita_id, barbero__barberia=request.user.barberia)
    except Cita.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Cita no encontrada'}, status=404)
        messages.error(request, "Cita no encontrada.")
        return redirect(request.META.get('HTTP_REFERER', 'agenda_citas'))

    # Opcional: validación adicional, como verificar si es el barbero o admin
    cita.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
     return JsonResponse({'success': True})
    messages.success(request, "La cita fue cancelada exitosamente.")
    return redirect(request.META.get('HTTP_REFERER', 'agenda_citas'))



