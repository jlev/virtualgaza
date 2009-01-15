from django.contrib import admin
import tour.models
import tour.widgets


class NeighborhoodAdmin(tour.widgets.GoogleAdmin):
	fields = ['name','population','bounds']
	default_lon = 34.451752
	default_lat = 31.44741
	default_zoom = 5

	
class BuildingAdmin(tour.widgets.GoogleAdmin):
	fields = ['name','model','buildingType','damage','location']
	default_lat = 31.44741
	default_lon = 34.451752
	default_zoom = 10
	
class EventAdmin(tour.widgets.GoogleAdmin):
	fields = ['time','kind','casualties','verified','location']
	default_lat = 31.44741
	default_lon = 34.451752
	default_zoom = 10

admin.site.register(tour.models.Neighborhood, NeighborhoodAdmin)
admin.site.register(tour.models.Building, BuildingAdmin)
admin.site.register(tour.models.BuildingType)
admin.site.register(tour.models.Event, EventAdmin)