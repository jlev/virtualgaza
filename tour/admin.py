from django.contrib import admin
from django import forms
from django.contrib.gis.gdal import SpatialReference,OGRGeometry
import tour.models
import tour.widgets

gaza = OGRGeometry('POINT (34.451752 31.44741)',4326)
gaza_sm = gaza.clone()
gaza_sm.transform_to(SpatialReference('EPSG:900913')) #convert to google spherical mercator

class CityAdmin(tour.widgets.GoogleAdmin):
	list_display = ['name']
	fields = ['name','population','bounds']
	default_lon = gaza_sm.coords[0]
	default_lat = gaza_sm.coords[1]
	default_zoom = 11
	debug = True

class NeighborhoodAdmin(tour.widgets.GoogleAdmin):
	list_display = ['name']
	fields = ['name','population','bounds']
	default_lon = gaza_sm.coords[0]
	default_lat = gaza_sm.coords[1]
	default_zoom = 11
	debug = True
	
class LocationAdmin(tour.widgets.GoogleAdmin):
	list_display = ['name']
	fields = ['name','coords']
	default_lon = gaza_sm.coords[0]
	default_lat = gaza_sm.coords[1]
	default_zoom = 12
	debug = True
	
class BuildingAdmin(tour.widgets.GoogleAdmin):
	fields = ['name','description','buildingType','url','damage','coords']
	default_lon = gaza_sm.coords[0]
	default_lat = gaza_sm.coords[1]
	default_zoom = 12


class BorderAdmin(tour.widgets.GoogleAdmin):
	fields = ['name','line']
	default_lon = gaza_sm.coords[0]
	default_lat = gaza_sm.coords[1]
	default_zoom = 11
	debug = True
	
class BombingAdmin(admin.ModelAdmin):
	list_display = ['name','time','kind','description','casualties','verified']
	exclude = ['coords']
	#don't display coords, we'll fill it in ourselves in the save method


admin.site.register(tour.models.Border,BorderAdmin)
admin.site.register(tour.models.City, CityAdmin)
admin.site.register(tour.models.Neighborhood, NeighborhoodAdmin)
admin.site.register(tour.models.Location, LocationAdmin)
admin.site.register(tour.models.Building, BuildingAdmin)
admin.site.register(tour.models.BuildingType)
admin.site.register(tour.models.Bombing, BombingAdmin)