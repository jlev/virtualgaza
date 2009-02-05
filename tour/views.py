from django.shortcuts import render_to_response, get_list_or_404,get_object_or_404
from django.template import RequestContext 
from django.conf import settings
from tour.models import Neighborhood,Location,Border,Bombing
from testimony.models import Author,Text,Video
from photologue.models import Gallery

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
	
	recent_text = Text.objects.all().filter(approved=True).order_by('-created_date')[:10]
	recent_galleries = Gallery.objects.filter(is_public=True).order_by('-date_added')[:2]
	recent_videos = Video.objects.all().filter(approved=True).order_by('-created_date')[:3]
	
	return render_to_response('base/frontpage.html', dict(mapDict,useMap="True",
								pageTitle="Break the Information Blockade",
								vectorLayers=layer_list,
								tooltipLayerName="Neighborhoods",
								polygonLayerName="Neighborhoods",
								zoomLayer="Border",
								posts=recent_text,
								photos=recent_galleries,
								videos=recent_videos,
								captionText="This site is currently under construction. We will add more data layers in the coming days."),
								context_instance = RequestContext(request)
							)

def neighborhood_page(request,nameSlug):
	humanName = deslug(nameSlug)
	authorList = Author.objects.filter(neighborhood__name__iexact=humanName).select_related()
	layerList = mapObjects(deslug(nameSlug))

	return render_to_response('tour/neighborhood_authors.html', dict(mapDict,useMap="True",
						pageTitle=humanName,
						theNeighborhood=humanName,
						authorList=authorList,
						vectorLayers=layerList,
						tooltipLayerName="Authors",
						zoomLayer="Neighborhoods"),
						context_instance = RequestContext(request))

def mapObjects(neighborhoodName):
	borderList = Border.objects.all()
	borders = []
	for b in borderList:
		borders.append(b.getJSON())
		
	if neighborhoodName == "all":
		neighborhoodList = Neighborhood.objects.all()
	else:
		neighborhoodList = Neighborhood.objects.all().filter(name__iexact=neighborhoodName)
	neighborhoods = []
	for n in neighborhoodList:
		neighborhoods.append(n.getJSON())
		
#	authors = []
#	for n in neighborhoodList:
#		authorList = Author.objects.filter(neighborhood__name__iexact=deslug(n.name))
#		for a in authorList:
#			authors.append(a.location.getJSON())
		
	bombingList = Bombing.objects.all()
	bombings = []
	for b in bombingList:
		bombings.append(b.getJSON())
	
	layer_list = [{'name':'Neighborhoods','list':neighborhoods,'styleName':'polygonStyleMap'},
								{'name':'Bombings','list':bombings,'styleName':'bombingStyleMap'},
								#{'name':'Authors','list':authors,'styleName':'pointStyleMap'},
								{'name':'Border','list':borders,'styleName':'lineStyleMap'},
							]
	return layer_list
