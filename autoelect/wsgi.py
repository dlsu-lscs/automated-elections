"""
WSGI config for autoelect project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "autoelect.settings")

# https_proxy = '127.0.0.1:8000'
# http_proxy = '127.0.0.1:8000'

# os.environ['https_proxy'] = https_proxy
# os.environ['http_proxy'] = http_proxy

application = get_wsgi_application()
