from django.shortcuts import render_to_response, get_list_or_404,get_object_or_404
from django.template import RequestContext 
from django.conf import settings
from tour.models import Neighborhood,Location,Border
from testimony.models import Author
from testimony.views import posts_by_recent

mapDict = { 'mapType':'G_SATELLITE_MAP',
			'googleAPIVersion':'2.x',
			'googleAPIKey':settings.GOOGLE_MAPS_API_KEY,
}

#stolen from http://code.unicoders.org/browser/hacks/trunk/enrico.py
def deslug(name):
	bits = name.split('-')
	bits[0] = bits[0].capitalize()
	return " ".join(bits)

def all_neighborhoods(request):
	borderList = Border.objects.all()
	borders = []
	for b in borderList:
		borders.append(b.getJSON())
		
	neighborhoodList = Neighborhood.objects.all()
	neighborhoods = []
	for n in neighborhoodList:
		neighborhoods.append(n.getJSON())
		
	authors = []
	for n in neighborhoodList:
		authorList = Author.objects.filter(neighborhood__name__iexact=deslug(n.name))
		for a in authorList:
			authors.append(a.location.getJSON())
	
	layer_list = [{'name':'Border','list':borders,'styleName':'lineStyleMap'},
								{'name':'Neighborhoods','list':neighborhoods,'styleName':'polygonStyleMap'},
								{'name':'Authors','list':authors,'styleName':'pointStyleMap'},
							]
	
	#recents = posts_by_recent(request,20)
	#del recents['Content-Type']
		#remove Content-Type, because we are inlining this response
	return render_to_response('base/base.html', dict(mapDict,
								pageTitle="Break the Information Blockade",
								vectorLayers=layer_list,
								tooltipLayerName="Authors",
								captionText="This site is currently under construction. We will add more data layers in the coming days."),
								context_instance = RequestContext(request)
							)

def one_neighborhood(request,nameSlug):
	humanName = deslug(nameSlug)
	theNeighborhood = get_object_or_404(Neighborhood,name__iexact=humanName)
	polygonList = [theNeighborhood.getJSON()]
	authorList = Author.objects.filter(neighborhood__name__iexact=humanName).select_related()
	pointList = []
	for a in authorList:
		pointList.append(a.location.getJSON())
	return render_to_response('tour/neighborhood_authors.html', dict(mapDict,
							vector_layer_name=humanName,poly_list=polygonList,
							author_layer_name="Authors",author_list=pointList),
							context_instance = RequestContext(request))
