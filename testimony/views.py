from django.shortcuts import render_to_response, get_list_or_404,get_object_or_404
from django.conf import settings
from testimony.models import Author,Text,Photograph,Video,Audio
from tour.models import Neighborhood

mapDict = { 'mapType':'G_SATELLITE_MAP',
			'googleAPIVersion':'2.x',
			'googleAPIKey':settings.GOOGLE_MAPS_API_KEY,
}

def deslug(name):
	bits = name.split('-')
	bits[0] = bits[0].capitalize()
	return " ".join(bits)

def authors_by_neighborhood(requst):
	theList = []
	neighborhood_list = Neighborhood.objects.all()
	for n in neighborhood_list:
		theList.append(n)
	author_list = Author.objects.all().select_related()
	
	point_list = []
	for a in author_list:
		point_list.append(a.location.coords.geojson)
	return render_to_response('testimony/all_authors.html',dict(mapDict,
				authors_unsorted=author_list,
				point_list=point_list)
			)

def author_by_full_name(request, firstName, lastName):
	"""Gets author by full name"""
	author = get_object_or_404(Author, first_name__iexact=deslug(firstName), last_name__iexact=deslug(lastName))
	posts = author.text_set.all()
	return render_to_response('testimony/author_detail.html',dict(mapDict,
				author=author,posts=posts,
				point_layer_name=author,
				point_list=[author.location.coords.geojson],
				poly_list=[])
			)

def author_by_id(request, id):
	"""Gets author by full name"""
	author = get_object_or_404(Author, id=id)
	return render_to_response('testimony/author_detail.html',dict(mapDict,
				author=author,
				point_list=[author.location.coords.geojson])
			)
	
def author_by_last_name(request, lastName):
	author_list = get_list_or_404(Author, last_name__iexact=deslug(lastName))
	point_list = []
	for a in author_list:
		point_list.append(a.location.coords.geojson)
	
	return render_to_response('testimony/author_by_name.html',dict(mapDict,
				author_list=author_list,
				point_list=point_list)
			)