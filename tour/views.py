from django.shortcuts import render_to_response, get_list_or_404,get_object_or_404
from django.template import RequestContext 
from django.conf import settings
from tour.models import Neighborhood,Location,Border
from testimony.models import Author

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
	lineList = []
	for b in borderList:
		lineList.append(b.getJSON())
	neighborhoodList = Neighborhood.objects.all()
	polygonList = []
	for n in neighborhoodList:
		polygonList.append(n.getJSON())
		
	#show all authors
	#may be slow with real data...
	pointList = []
	for n in neighborhoodList:
		authorList = Author.objects.filter(neighborhood__name__iexact=deslug(n.name))
		for a in authorList:
			pointList.append(a.location.getJSON())
	return render_to_response('base/base.html', dict(mapDict,
								pageTitle="Break the Information Blockade",
								vector_layer_name="Neighborhoods",poly_list=polygonList,
								point_layer_name="Authors",point_list=pointList,
								line_layer_name="Border",line_list=lineList,
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
							point_layer_name="Testimony",point_list=pointList),
							 context_instance = RequestContext(request))
