from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = "Crea un superusuario automáticamente usando variables de entorno"

    def handle(self, *args, **kwargs):
        self.stdout.write("🧪 Ejecutando createsu...")

        User = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not username or not email or not password:
            self.stdout.write(self.style.ERROR("❌ Faltan variables de entorno necesarias (usuario, email o contraseña)."))
            return

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS("✅ Superusuario creado correctamente"))
        else:
            self.stdout.write("⚠️ El superusuario ya existe")
