"""
WSGI config for barber project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.contrib.auth import get_user_model
import django
from django.core.management import call_command


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barber.settings')

application = get_wsgi_application()

if os.environ.get('RENDER_CREATE_SUPERUSER') == 'true':
    User = get_user_model()
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)


