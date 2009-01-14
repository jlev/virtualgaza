from django.contrib.gis import admin
from django.contrib.gis.maps.google import GoogleMap
from django.conf import settings

# stolen from http://www.djangosnippets.org/snippets/1144/
class GoogleAdmin(admin.OSMGeoAdmin):
	GMAP = GoogleMap(key=settings.GOOGLE_MAPS_API_KEY,version='2.x')
	extra_js = [GMAP.api_url + GMAP.key]
	map_template = 'gis/admin/google.html'
	
	#override defaults in OSMGeoAdmin
	save_as = True
	scrollable = True
	map_width = 800
	map_height = 600
	debug = True