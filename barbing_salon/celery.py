from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import ssl

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbing_salon.settings')

app = Celery('barbing_salon')

# Configure Celery with Redis and SSL
app.conf.update(
    broker_url=os.getenv('CELERY_BROKER_URL'),  # Use the provided broker URL
    result_backend=os.getenv('CELERY_RESULT_BACKEND'),  # Use the provided result backend URL
    broker_use_ssl={
        'cert_reqs': ssl.CERT_REQUIRED,  # Ensure the Redis server certificate is verified
        # Optionally specify CA, keyfile, and certfile paths if needed
    },
    result_backend_transport_options={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,  # Ensure the Redis server certificate is verified
        # Optionally specify CA certs if needed
    },
    broker_transport_options={
        'visibility_timeout': 3600,  # Adjust as needed
        'socket_timeout': 30,  # Adjust as needed
    },
)

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
