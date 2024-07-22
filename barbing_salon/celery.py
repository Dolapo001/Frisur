# your_project/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

from barbing_salon import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbing_salon.settings')

app = Celery('barbing_salon')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
#app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks()
