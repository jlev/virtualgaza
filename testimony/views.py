from django.shortcuts import render_to_response, get_list_or_404,get_object_or_404
from django.template import RequestContext 
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

def authors_by_neighborhood(request):
	theList = []
	neighborhood_list = Neighborhood.objects.all()
	for n in neighborhood_list:
		theList.append(n)
	author_list = Author.objects.all().select_related()
	
	point_list = []
	for a in author_list:
		point_list.append(a.location.getJSON())
	return render_to_response('testimony/authors_by_neighborhood.html',dict(mapDict,
				authors_unsorted=author_list,
				point_list=point_list),
			context_instance = RequestContext(request))

def author_by_full_name(request, firstName, lastName):
	"""Gets author by full name"""
	author = get_object_or_404(Author, first_name__iexact=deslug(firstName), last_name__iexact=deslug(lastName))
	posts = author.text_set.all()
	return render_to_response('testimony/author_detail.html',dict(mapDict,
				author=author,posts=posts,
				point_layer_name=author,
				point_list=[author.location.getJSON()],
				poly_list=[]),
			context_instance = RequestContext(request))

def author_by_id(request, id):
	"""Gets author by full name"""
	author = get_object_or_404(Author, id=id)
	return render_to_response('testimony/author_detail.html',dict(mapDict,
				author=author,
				point_list=[author.location.getJSON()]),
			context_instance = RequestContext(request))
	
def author_by_last_name(request, lastName):
	author_list = get_list_or_404(Author, last_name__iexact=deslug(lastName))
	point_list = []
	for a in author_list:
		point_list.append(a.location.getJSON())
	
	return render_to_response('testimony/authors_by_name.html',dict(mapDict,
				author_list=author_list,
				point_list=point_list),
			context_instance = RequestContext(request))

def posts_by_author(request, firstName, lastName):
	first = deslug(firstName)
	last = deslug(lastName)
	posts=get_list_or_404(Text,author__first_name__iexact=first,
					author__last_name__iexact=last,approved=1)

	return render_to_response('testimony/post_list.html',
						{'first_name':first,'last_name':last,
						'postList':posts},
						context_instance = RequestContext(request))

def posts_by_author_and_year(request, firstName, lastName, year):
	first = deslug(firstName)
	last = deslug(lastName)
	posts=get_list_or_404(Text,author__first_name__iexact=first,
					author__last_name__iexact=last,
					created_date__year=year,approved=1)

	return render_to_response('testimony/post_list.html',
						{'first_name':first,'last_name':last,
						'year':year,
						'postList':posts},
					context_instance = RequestContext(request))

def posts_by_author_and_month(request, firstName, lastName, year, month):
	first = deslug(firstName)
	last = deslug(lastName)
	posts=get_list_or_404(Text,author__first_name__iexact=first,
					author__last_name__iexact=last,
					created_date__year=year,
					created_date__month=month,
					approved=1)

	return render_to_response('testimony/post_list.html',
						{'first_name':first,'last_name':last,
						'year':year,'month':month,
						'postList':posts},
					context_instance = RequestContext(request))

def posts_by_author_and_date(request, firstName, lastName, year, month, day):
	first = deslug(firstName)
	last = deslug(lastName)
	posts=get_list_or_404(Text,author__first_name__iexact=first,
					author__last_name__iexact=last,
					created_date__year=year,
					created_date__month=month,
					created_date__day=day,
					approved=1)
					
	return render_to_response('testimony/post_list.html',
						{'first_name':first,'last_name':last,
						'year':year,'month':month,'day':day,
						'postList':posts},
				context_instance = RequestContext(request))
			
def posts_by_recent(request, num_latest):
	posts=Text.objects.all().filter(approved=1).order_by('created_date')[:num_latest]
	#abuse the name and year fields of the template for title display
	return render_to_response('testimony/post_list.html',
				{'first_name':'Most','last_name':'Recent','year':num_latest,
					'postList':posts},
				context_instance = RequestContext(request))

