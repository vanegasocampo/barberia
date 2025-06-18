from django.urls import path
from . import views
from .views import CalendarioView, citas_json

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('barberos/', views.BarberoListView.as_view(), name='barbero_list'),
    path('barberos/crear/', views.BarberoCreateView.as_view(), name='barbero_create'),
    path('barberos/<int:pk>/editar/', views.BarberoUpdateView.as_view(), name='barbero_update'),
    path('barberos/<int:pk>/eliminar/', views.BarberoDeleteView.as_view(), name='barbero_delete'),
    path('servicios/', views.ServicioListView.as_view(), name='servicio_list'),
    path('servicios/crear/', views.ServicioCreateView.as_view(), name='servicio_create'),
    path('servicios/<int:pk>/editar/', views.ServicioUpdateView.as_view(), name='servicio_update'),
    path('servicios/<int:pk>/eliminar/', views.ServicioDeleteView.as_view(), name='servicio_delete'),
    path('agenda/', views.AgendaView.as_view(), name='agenda'),
    path('webhook/whatsapp/', views.whatsapp_webhook, name='whatsapp_webhook'),
    path('calendario/', CalendarioView.as_view(), name='calendario'),
    path('api/calendario/', citas_json, name='citas_json'),  
    path('citas/cancelar/', views.cancelar_cita, name='cancelar_cita'),
]
