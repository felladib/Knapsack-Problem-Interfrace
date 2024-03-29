from django.contrib import admin

# Register your models here.

from .models import objet, sacados  # Importez les modèles depuis votre application

admin.site.register(objet)
admin.site.register(sacados)