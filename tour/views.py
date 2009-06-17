from django.shortcuts import render_to_response, get_list_or_404,get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext 
from django.conf import settings
from tour.models import City,Neighborhood,Location,Border,Bombing
from testimony.models import Author,Text,Video
from photologue.models import Gallery,Photo
from django.contrib.gis import geos

mapDict = { 'mapType':'G_SATELLITE_MAP',
			'googleAPIVersion':'2.x',
			'googleAPIKey':settings.GOOGLE_MAPS_API_KEY,
}

#stolen from http://code.unicoders.org/browser/hacks/trunk/enrico.py
def deslug(name):
	bits = name.split('-')
	for i in range(0,len(bits)):
		bits[i] = bits[i].capitalize()
	return " ".join(bits)

def frontpage(request):
	layer_list = mapObjects("all")

	return render_to_response('base/frontpage.html',
					dict(mapDict,useMap="True",
							pageTitle="Break the Information Blockade",
							vectorLayers=layer_list,
							polygonLayerName="Neighborhoods",
							popupLayerName="Bombings",
							),
							context_instance = RequestContext(request))

def neighborhoods_within_bounds(request):
	if request.is_ajax() and request.method == 'POST':
		try:
			bnds = geos.fromstr(request.POST.get('bounds'))
		except (TypeError,ValueError),error:
			msg = "Didn't get a valid bounds in POST." + str(error)
			return HttpResponse(msg)
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
			neighborhoodList = neighborhoodList[:4]
			neighborhoodList[3].name = "..."

		return render_to_response('tour/neighborhood_ajax_request.html',locals())
	else:
		msg = "Didn't get AJAX request. You are probably a robot; move along."
		return HttpResponse(msg)

def neighborhood_page(request,nameSlug):
	humanName = deslug(nameSlug)
	authorList = Author.objects.filter(neighborhood__name__iexact=humanName).select_related()
	recentPosts=Text.objects.all().filter(neighborhood__name__iexact=humanName,approved=1).order_by('-created_date')[:5]
	layerList = mapObjects(deslug(nameSlug))
	galleryList = Gallery.objects.filter(tags__iexact=u'"%s"' % humanName,is_public=True)
	videoList = Video.objects.filter(neighborhood__name__iexact=humanName,approved=True)

	return render_to_response('tour/neighborhood.html', dict(mapDict,useMap="True",mapNavigate="True",
						pageTitle=humanName,
						theNeighborhood=humanName,
						authorList=authorList,
						recentPosts=recentPosts,
						vectorLayers=layerList,
						galleryList=galleryList,
						videoList=videoList,
						popupLayerName="Bombings",
						showDamage="True",
						zoomLayer="Neighborhoods"),
						context_instance = RequestContext(request))

def mapObjects(neighborhoodName):
	borderList = Border.objects.all()
	borders = []
	for b in borderList:
		borders.append(b.getJSON())
		
	cityList = City.objects.all()
	cities = []
	for c in cityList:
		cities.append(c.getJSON())
		
	if neighborhoodName == "all":
		neighborhoodList = Neighborhood.objects.all()
	else:
		neighborhoodList = Neighborhood.objects.all().filter(name__iexact=neighborhoodName)
	neighborhoods = []
	for n in neighborhoodList:
		neighborhoods.append(n.getJSON())
		
	bombingList = Bombing.objects.all()
	bombings = []
	for b in bombingList:
		bombings.append(b.getJSON())
	
	layer_list = [
		{'name':'Cities',
			'list':cities,
			'styleName':'polygonStyleMap'},
		{'name':'Neighborhoods',
			'list':neighborhoods,
			'styleName':'polygonStyleMap'},
		{'name':'Border',
		'list':borders,
		'styleName':'lineStyleMap'},
		{'name':'Bombings',
		'list':bombings,
		'styleName':'bombingStyleMap'}
	]
	return layer_list