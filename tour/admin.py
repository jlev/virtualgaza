from django.contrib import admin
from django.contrib.gis.gdal import SpatialReference,CoordTransform,OGRGeometry
import tour.models
import tour.widgets

gaza = OGRGeometry('POINT (34.451752 31.44741)',4326)
gaza_sm = gaza.clone()
gaza_sm.transform_to(SpatialReference('EPSG:900913')) #convert to google spherical mercator

class NeighborhoodAdmin(tour.widgets.GoogleAdmin):
	fields = ['name','population','bounds']
	default_lon = gaza_sm.coords[0]
	default_lat = gaza_sm.coords[1]
	default_zoom = 11
	debug = True
	
class LocationAdmin(tour.widgets.GoogleAdmin):
	fields = ['name','coords']
	default_lon = gaza_sm.coords[0]
	default_lat = gaza_sm.coords[1]
	default_zoom = 12
	debug = True
	
class BuildingAdmin(tour.widgets.GoogleAdmin):
	fields = ['name','model','buildingType','damage','coords']
	default_lon = gaza_sm.coords[0]
	default_lat = gaza_sm.coords[1]
	default_zoom = 12
	
class EventAdmin(tour.widgets.GoogleAdmin):
	fields = ['time','kind','casualties','verified','coords']
	default_lon = gaza_sm.coords[0]
	default_lat = gaza_sm.coords[1]
	default_zoom = 12

admin.site.register(tour.models.Neighborhood, NeighborhoodAdmin)
admin.site.register(tour.models.Location, LocationAdmin)
admin.site.register(tour.models.Building, BuildingAdmin)
admin.site.register(tour.models.BuildingType)
admin.site.register(tour.models.Event, EventAdmin)