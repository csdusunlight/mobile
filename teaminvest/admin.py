from django.contrib import admin
from teaminvest.models import Project
from django.contrib.admin.options import ModelAdmin

# Register your models here.
class ProjectAdmin(ModelAdmin):
    search_fields = ('title',)
admin.site.register(Project, ProjectAdmin)