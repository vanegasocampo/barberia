from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = "Crea un superusuario automáticamente usando variables de entorno"

    def handle(self, *args, **kwargs):
        print("🧪 Ejecutando createsu...")  # Agregado para depuración

        User = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            print("✅ Superusuario creado correctamente")
        else:
            print("⚠️ El superusuario ya existe")
