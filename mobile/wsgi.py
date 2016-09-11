"""
WSGI config for mobile project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mobile.settings")
os.environ.setdefault("PYTHON_EGG_CACHE", "/tmp/.python-eggs")
application = get_wsgi_application()