from django.shortcuts import render_to_response
from django.template import RequestContext 
from django.conf import settings

from django.contrib.gis.geos import *
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
		bnds = fromstr(request.POST.get('bounds'))
		neighborhoodsWithinBounds = Neighborhood.objects.filter(bounds__intersects=bnds)
		
		neighborhoodList = []
		for n in neighborhoodsWithinBounds:
			if n.hasContent():
				neighborhoodList.append(n)
		
		recentPosts = Text.objects.filter(approved=True,neighborhood__in=neighborhoodList).order_by('-created_date')[:5]
		
		#because gallery neighborhood lookups use tags, we can't use the neighborhood__in syntax
		#have to concat QuerySets manually
		photos = Gallery.objects.none()
		for n in neighborhoodList:
			photos = photos | Gallery.objects.filter(tags__iexact=u'"%s"' % n.name,is_public=True)
		
		photos.order_by('-date_added')[:2]
		#list concat turned into SQL, so won't raise error

		videos = Video.objects.filter(neighborhood__in=neighborhoodList).order_by('-created_date')[:3]
		return render_to_response('tour/test_ajax_request.html',locals())
