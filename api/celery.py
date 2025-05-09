# api/celery.py

from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
#from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

app = Celery('api')  # Replace 'your_project' with your project name

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
#app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    #print(f'Request: {self.request}')

# Optional: Configure Celery Beat if you installed django-celery-beat
#CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

