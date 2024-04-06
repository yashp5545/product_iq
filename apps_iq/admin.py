from django.contrib import admin

# Register your models here.

from .models import App, Module, Challenge, Level, LevelResponses

admin.site.register(App)
admin.site.register(Module)
admin.site.register(Challenge)
admin.site.register(Level)
admin.site.register(LevelResponses)
