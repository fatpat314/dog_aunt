from django.contrib import admin
from .models import Venue
from .models import DogAuntUser
from .models import Event

admin.site.register(Venue)
admin.site.register(DogAuntUser)
admin.site.register(Event)
