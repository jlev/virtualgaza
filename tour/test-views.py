from django.shortcuts import render_to_response
from django.template import RequestContext 
from django.conf import settings

from django.contrib.gis.geos import *
from tour.models import Neighborhood

from virtualgaza.tour.views import mapObjects

mapDict = { 'mapType':'G_SATELLITE_MAP',
			'googleAPIVersion':'2.x',
			'googleAPIKey':settings.GOOGLE_MAPS_API_KEY,
}

def test_frontpage(request):
	layer_list = mapObjects("all")
	return render_to_response('tour/test_frontpage.html',
					dict(mapDict,useMap="True",
							pageTitle="Test Frontpage",
							vectorLayers=layer_list,
							polygonLayerName="Neighborhoods",
							),
							context_instance = RequestContext(request))

def neighborhoods_within_bounds(request):
	if request.is_ajax() and request.method == 'POST':
		#print request.POST
		bnds = fromstr(request.POST.get('bounds'))
		neighborhoodList = Neighborhood.objects.filter(bounds__intersects=bnds)
		#print neighborhoodList
	return render_to_response('tour/test_ajax_request.html',locals())
