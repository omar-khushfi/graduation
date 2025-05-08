from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Folder)
admin.site.register(Word)
admin.site.register(Language)
admin.site.register(Translate)