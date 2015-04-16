from django.contrib import admin

# Register your models here.

from django.contrib import admin
from models import VizProject
from models import VizLayer

class VizLayerInline(admin.TabularInline):
  model = VizProject.layers.through 
  extra = 1

class VizProjectAdmin(admin.ModelAdmin):
  list_display = ('project_name', 'project_description', 'public')
  exclude = ('layers',)
  inlines = [
      VizLayerInline,
  ]

admin.site.register(VizProject, VizProjectAdmin)

class VizLayerAdmin(admin.ModelAdmin):
  list_display = ('layer_name', 'token', 'channel')

admin.site.register(VizLayer, VizLayerAdmin)
