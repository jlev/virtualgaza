from django.shortcuts import render_to_response, get_list_or_404,get_object_or_404
from testimony.models import Author,Text,Photograph,Video,Audio
from tour.models import Neighborhood

def index(request):
	return render_to_response('base/base.html', {'content':"front page"})

def all_authors(requst):
	neighborhood_list = get_list_or_404(Neighborhood)
	author_list = get_list_or_404(Author)
	return render_to_response('testimony/all_authors.html', {'author_list': author_list, 'neighborhood_list':neighborhood_list})

def author_by_full_name(request, firstName, lastName):
	"""Gets author by full name"""
	author = get_object_or_404(Author, first_name__iexact=firstName, last_name__iexact=lastName)
	posts = author.text_set.all()
	return render_to_response('testimony/author_detail.html', {'author':author, 'posts':posts})
	
def author_by_id(request, id):
	"""Gets author by full name"""
	author = get_object_or_404(Author, id=id)
	return render_to_response('testimony/author_detail.html', {'author':author})
	
def author_by_last_name(request, lastName):
	author_list = get_list_or_404(Author, last_name__iexact=lastName)
	return render_to_response('testimony/author_by_name.html', {'author_list': author_list})