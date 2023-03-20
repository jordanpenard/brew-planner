from django.contrib import admin
from .models import Grain, Hop, Yeast, Stock

admin.site.register(Grain)
admin.site.register(Hop)
admin.site.register(Yeast)
admin.site.register(Stock)
