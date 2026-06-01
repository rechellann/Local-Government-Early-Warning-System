"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import logging

from django.core.wsgi import get_wsgi_application
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

logger = logging.getLogger(__name__)

# Initialize Django ASGI application
application = get_wsgi_application()

# Middleware wrapper for production monitoring
if not settings.DEBUG:
    from whitenoise.wsgi import WhiteNoise
    application = WhiteNoise(application, root=settings.STATIC_ROOT)
    logger.info('✓ Production WSGI configured with WhiteNoise static file serving')
