import inspect
from django.contrib import admin
from django.db import models
from .models import *


# just register all models for now
__models_module = '.'.join(__name__.split('.')[:-1] + ['models'])
_models = [m for m in locals().values()
           if inspect.isclass(m)
           and m.__module__ == __models_module
           and issubclass(m, models.Model)
           and not (m._meta.abstract or m._meta.proxy)]
for model in _models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
