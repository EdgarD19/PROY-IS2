from django.contrib import admin
from .models import EspacioTrabajo, Tablero, Lista, Tarjeta

# Register your models here.
admin.site.register(EspacioTrabajo)
admin.site.register(Tablero)
admin.site.register(Lista)
admin.site.register(Tarjeta)

