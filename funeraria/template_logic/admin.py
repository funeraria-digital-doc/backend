from django.contrib import admin
from template_logic.models import TemplateLogic

@admin.register(TemplateLogic)
class TemplateLogicAdmin(admin.ModelAdmin):
    list_display = ['title', 'file', 'group']
