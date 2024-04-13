from django.contrib import admin

# Register your models here.

from .models import App, Module, Challenge, Level, LevelResponses, Categories, SkillResponses, Skill, Section, Topic, Lession

admin.site.register(App)
admin.site.register(Module)
admin.site.register(Challenge)
admin.site.register(Level)
admin.site.register(LevelResponses)


admin.site.register(Categories)
admin.site.register(Skill)
admin.site.register(SkillResponses)


admin.site.register(Section)
admin.site.register(Topic)
admin.site.register(Lession)
