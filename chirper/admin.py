from django.contrib import admin

from chirper.models import UserProfile, Chirp

admin.site.register(UserProfile)
admin.site.register(Chirp)
