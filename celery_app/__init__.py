import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rainforest_ecom.settings")
app = Celery("rainforest_ecom")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
__all__ = ("app",)
