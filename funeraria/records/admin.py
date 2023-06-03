from django.contrib import admin

from records.models import Record

@admin.register(Record)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'dead_location']
