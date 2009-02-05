from django.conf import settings
from django.http import HttpResponse,Http404
from django.shortcuts import render_to_response, get_list_or_404,get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext 

from testimony.models import Author,Text,Video,Audio
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
	author_list = []
	all_authors = Author.objects.all().order_by('last_name').select_related()
	
	for a in all_authors:
		author_list.append({'first_name':a.first_name,'last_name':a.last_name,
			'neighborhood':a.neighborhood.name})
	
	return render_to_response('testimony/authors_by_neighborhood.html',dict(mapDict,
				author_list=author_list),
			context_instance = RequestContext(request))

def author_by_full_name(request, firstName, lastName):
	"""Gets author by full name"""
	author = get_object_or_404(Author, first_name__iexact=deslug(firstName), last_name__iexact=deslug(lastName))
	posts = author.text_set.all().filter(approved=1).order_by('-created_date')
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
	posts=Text.objects.all().filter(author__first_name__iexact=first,
					author__last_name__iexact=last,approved=1).order_by('-created_date')

	return render_to_response('testimony/post_list.html',
						{'first_name':first,'last_name':last,
						'postList':posts},
						context_instance = RequestContext(request))

def posts_by_author_and_year(request, firstName, lastName, year):
	first = deslug(firstName)
	last = deslug(lastName)
	posts=Text.objects.all().filter(author__first_name__iexact=first,
					author__last_name__iexact=last,created_date__year=year,approved=1).order_by('-created_date')

	nextLink= "/author/%s_%s/%s/" % (firstName,lastName,int(year)+1)
	prevLink = "/author/%s_%s/%s/" % (firstName,lastName,int(year)-1)

	return render_to_response('testimony/post_list.html',
						{'first_name':first,'last_name':last,
						'year':year,
						'postList':posts,
						'next':nextLink,'prev':prevLink,'dateType':'year'},
					context_instance = RequestContext(request))

def posts_by_author_and_month(request, firstName, lastName, year, month):
	first = deslug(firstName)
	last = deslug(lastName)
	posts=Text.objects.all().filter(author__first_name__iexact=first,
					author__last_name__iexact=last,
					created_date__year=year,created_date__month=month,
					approved=1).order_by('-created_date')

	nextLink= "/author/%s_%s/%s/%s/" % (firstName,lastName,year,int(month)+1)
	prevLink = "/author/%s_%s/%s/%s/" % (firstName,lastName,year,int(month)-1)

	return render_to_response('testimony/post_list.html',
						{'first_name':first,'last_name':last,
						'year':year,'month':month,
						'postList':posts,
						'next':nextLink,'prev':prevLink,'dateType':'month'},
					context_instance = RequestContext(request))

def posts_by_author_and_date(request, firstName, lastName, year, month, day):
	first = deslug(firstName)
	last = deslug(lastName)
	posts=Text.objects.all().filter(author__first_name__iexact=first,
					author__last_name__iexact=last,
					created_date__year=year,
					created_date__month=month,
					created_date__day=day,
					approved=1).order_by('-created_date')
	
	num_posts = posts.count()
	if num_posts == 0:
		raise Http404
	if num_posts > 1:
		firstPostToday = posts[0]
		lastPostToday = posts[num_posts-1]
	else:
		firstPostToday = posts[0]
		lastPostToday = posts[0]
		
	try:
		nextPost = lastPostToday.get_next_by_created_date(author__first_name__iexact=first,author__last_name__iexact=last,approved=1)
		nextLink= "/author/%s_%s/%s/%s/%s/" % (firstName,lastName,nextPost.created_date.year,nextPost.created_date.month,nextPost.created_date.day)
	except ObjectDoesNotExist:
		nextLink = ""
		
	try:
		prevPost = firstPostToday.get_previous_by_created_date(author__first_name__iexact=first,author__last_name__iexact=last,approved=1)
		prevLink = "/author/%s_%s/%s/%s/%s/" % (firstName,lastName,prevPost.created_date.year,prevPost.created_date.month,prevPost.created_date.day)
	except ObjectDoesNotExist:
		prevLink = ""

	return render_to_response('testimony/post_list.html',
						{'first_name':first,'last_name':last,
						'year':year,'month':month,'day':day,
						'postList':posts,
						'next':nextLink,'prev':prevLink,'dateType':'day'},
				context_instance = RequestContext(request))
			
def posts_by_recent(request, num_latest):
	posts=Text.objects.all().filter(approved=1).order_by('-created_date')[:num_latest]
	#abuse the name and year fields of the template for title display
	return render_to_response('testimony/post_titles.html',
				{'first_name':'Most','last_name':'Recent','year':num_latest,
					'postList':posts},
				context_instance = RequestContext(request))

def all_posts(request):
	posts=Text.objects.all().filter(approved=1).order_by('-created_date')
	#abuse the name and year fields of the template for title display
	return render_to_response('testimony/post_titles.html',
				{'first_name':'All','last_name':'Testimony',
					'postList':posts},
				context_instance = RequestContext(request))
				
		
def search_for_author(request):
	#make this searchable
	html = "<html><body>Click an author on the map to see their posts here</body></html>"
	return HttpResponse(html)
	
def all_videos(request):
	videos=Video.objects.all().filter(approved=1).order_by('-created_date')
	return render_to_response('testimony/video.html',{'videoList':videos},
				context_instance = RequestContext(request))
				
def recent_videos(request, num_latest):
	videos=Video.objects.all().filter(approved=1).order_by('-created_date')[:num_latest]
	return render_to_response('testimony/video.html',{'videoList':videos},
				context_instance = RequestContext(request))
				
def video_by_date(request, year, month, day):
	videos=Video.objects.all().filter(created_date__year=year,
					created_date__month=month,created_date__day=day,approved=1).order_by('-created_date')
	if videos.count() == 0 :
		raise Http404
	return render_to_response('testimony/video.html',{'videoList':videos},
				context_instance = RequestContext(request))