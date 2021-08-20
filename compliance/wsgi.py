"""
WSGI config for cobranca project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import signal
import sys
import traceback
from datetime import time

from django.core.wsgi import get_wsgi_application

# os.environ['DJANGO_SETTINGS_MODULE'] = 'compliance.settings'

# application = get_wsgi_application()

sys.path.append('/var/www/compliance/app')
sys.path.append('/var/www/compliance/venv/lib/python3.8/site-packages')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "compliance.settings")

try:
    application = get_wsgi_application()
except Exception:
    # Error loading applications
    if 'mod_wsgi' in sys.modules:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)
