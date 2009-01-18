from django.shortcuts import render_to_response, get_list_or_404,get_object_or_404
from django.conf import settings
from tour.models import Neighborhood,Location
from testimony.models import Author

mapDict = { 'mapType':'G_HYBRID_MAP',
			'googleAPIVersion':'2.x',
			'googleAPIKey':settings.GOOGLE_MAPS_API_KEY,
}

#stolen from http://code.unicoders.org/browser/hacks/trunk/enrico.py
def deslugify(name):
	bits = name.split('-')
	bits[0] = bits[0].capitalize()
	return " ".join(bits)

def all_neighborhoods(request):
	neighborhoodList = Neighborhood.objects.all()
	polygonList = []
	for n in neighborhoodList:
		polygonList.append(n.bounds.geojson)
		
	#show all authors
	#may be slow with real data...
	pointList = []
	for n in neighborhoodList:
		authorList = Author.objects.filter(neighborhood__name__iexact=deslugify(n.name))
		for a in authorList:
			pointList.append(a.location.coords.geojson)
	return render_to_response('base/base.html', dict(mapDict,
								pageTitle="Break the Information Blockade",
								vector_layer_name="Neighborhoods",poly_list=polygonList,
								point_layer_name="Authors",point_list=pointList)
							)

def one_neighborhood(request,nameSlug):
	humanName = deslugify(nameSlug)
	theNeighborhood = get_object_or_404(Neighborhood,name__iexact=humanName)
	polygonList = [theNeighborhood.bounds.geojson]
	authorList = Author.objects.filter(neighborhood__name__iexact=humanName).select_related()
	pointList = []
	for a in authorList:
		pointList.append(a.location.coords.geojson)
	return render_to_response('tour/neighborhood_authors.html', dict(mapDict,
							vector_layer_name=humanName,poly_list=polygonList,
							point_layer_name="Testimony",point_list=pointList)
							)
