from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import ssl

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbing_salon.settings')

app = Celery('barbing_salon')

# Configure Celery with Redis and SSL
app.conf.update(
    broker_url=os.getenv('CELERY_BROKER'),
    result_backend=os.getenv('CELERY_BACKEND'),
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,  # or ssl.CERT_OPTIONAL or ssl.CERT_NONE
    },
    result_backend_transport_options={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,  # or ssl.CERT_OPTIONAL or ssl.CERT_NONE
    },
)

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
