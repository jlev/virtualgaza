from django.shortcuts import render_to_response
from django.template import RequestContext 
from django.conf import settings

from django.contrib.gis import geos
from tour.models import Neighborhood
from testimony.models import Author,Text,Video
from photologue.models import Gallery

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
							popupLayerName="Bombings",
							),
							context_instance = RequestContext(request))

def neighborhoods_within_bounds(request):
	if request.is_ajax() and request.method == 'POST':
		bnds = geos.fromstr(request.POST.get('bounds'))
		neighborhoodsWithinBounds = Neighborhood.objects.filter(bounds__intersects=bnds)
		
		neighborhoodList = []
		for n in neighborhoodsWithinBounds:
			if n.hasContent():
				neighborhoodList.append(n)
		
		posts = Text.objects.filter(approved=True,neighborhood__in=neighborhoodList).order_by('-created_date')
		
		#because gallery neighborhood lookups use tags, we can't use the neighborhood__in syntax
		#have to concat QuerySets manually
		photos = Gallery.objects.none()
		for n in neighborhoodList:
			photos = photos | Gallery.objects.filter(tags__iexact=u'"%s"' % n.name,is_public=True)
		photos = photos.order_by('-date_added')

		videos = Video.objects.filter(neighborhood__in=neighborhoodList).order_by('-created_date')
		
		#slice lists if we have a lot of neighborhoods
		if (len(neighborhoodList) > 3):
			posts = posts[:5]
			photos = photos[:2]
			videos = videos[:3]
			neighborhoodList = neighborhoodList[:3]
			neighborhoodList.append("...")
		
		return render_to_response('tour/test_ajax_request.html',locals())
