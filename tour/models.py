# coding=utf8
#for the unicode strings in Bombing.save()

from django.contrib.gis.db import models
from django.template.defaultfilters import slugify
from django.contrib.gis.gdal import SpatialReference,OGRGeometry
from testimony.models import Author,Text,Video
from photologue.models import Gallery,Photo
from exceptions import UnicodeEncodeError

theSRID = 900913

def deslug(name):
	bits = name.split('-')
	bits[0] = bits[0].capitalize()
	return " ".join(bits)

class Location(models.Model):
	name = models.CharField(max_length=100,unique=True)
	coords = models.PointField(srid=theSRID)
	objects = models.GeoManager()
	
	def getJSON(self):
		first,last = str(self.name).split('_')
		firstName = deslug(first)
		lastName = deslug(last)
		
		json = {}
		json['type']='Feature'
		json['geometry'] = eval(self.coords.geojson)
		json['properties'] = {'name':str(self.name),'displayName':str(firstName + " " + lastName)}	
		return str(json)
	def __unicode__(self):
		return self.name
		
class Border(models.Model):
	name = models.CharField(max_length=100)
	line = models.LineStringField(srid=theSRID)
	objects = models.GeoManager()
	
	def getJSON(self):
		json = {}
		json['type']='Feature'
		json['geometry'] = eval(self.line.geojson)
		json['properties'] = {'name':str(self.name)}
		return str(json)
	def __unicode__(self):
		return self.name

class City(models.Model):
	'''A city'''
	name = models.CharField(max_length=50)
	bounds = models.PolygonField(srid=theSRID)
	population = models.IntegerField(blank=True,null=True)
	objects = models.GeoManager()
	
	def getJSON(self):
		json = {}
		json['type']='Feature'
		json['geometry'] = eval(self.bounds.geojson)
		json['properties'] = {'name':str(self.name)}
		return str(json)
	
	def __unicode__(self):
		return self.name
		
	class Meta:
		verbose_name_plural = 'cities'

class Neighborhood(models.Model):
	'''A local neighborhood'''
	name = models.CharField(max_length=50)
	bounds = models.PolygonField(srid=theSRID)
	population = models.IntegerField(blank=True,null=True)
	objects = models.GeoManager()
	
	def numPosts(self):
		return Text.objects.filter(neighborhood__name__iexact=self.name).count()
	def numPhotos(self):
		return Gallery.objects.filter(tags__iexact=u'"%s"' % self.name,is_public=True).count()
	def numVideos(self):
		return Video.objects.filter(neighborhood__name__iexact=self.name,approved=True).count()
	def numAuthors(self):
		return Author.objects.filter(neighborhood__name__iexact=self.name).count()

	def hasContent(self):
		if ((self.numPosts() == 0) and (self.numPhotos() == 0) and (self.numVideos() == 0)):
			return False
		else:
			return True
	
	def getJSON(self):
		json = {}
		json['type']='Feature'
		json['geometry'] = eval(self.bounds.geojson)
		json['properties'] = {'name':str(self.name),
							'numAuthors':str(self.numAuthors()),
							'numPosts':str(self.numPosts()),
							'numPhotos':str(self.numPhotos()),
							'numVideos':str(self.numVideos()),
							'link':str("/neighborhood/%s" %slugify(self.name))}
		return str(json)
	
	def __unicode__(self):
		return self.name

	def getRandomLocationWithin(self,theName):
		bounds = self.bounds.boundary.coords
		#extent doesn't seem to work on the linestring, so do it manually
		(xbounds,ybounds) = ([],[])
		for b in bounds:
			xbounds.append(b[0])
			ybounds.append(b[1])
		(xmin,ymin) = (min(xbounds),min(ybounds))
		(xmax,ymax) = (max(xbounds),max(ybounds))
		
		#smarter way to do this?
		goodLoc = False
		tries = 0
		import random
		while (not goodLoc):
			randLat = random.uniform(xmin,xmax)
			randLon = random.uniform(ymin,ymax)
			thePoint = 'SRID=%s;POINT(%f %f)' % (theSRID, randLat, randLon)
			contains = Neighborhood.objects.filter(bounds__contains=thePoint)
			tries += 1
			if (contains.__len__() != 0):
				goodLoc = True
#		print "found random point after",tries,"tries"
		l = Location(name=theName,coords=thePoint)
		l.save()
		return l
		
class BuildingType(models.Model):
	name = models.CharField(max_length=50)
	mapPin = models.ImageField(upload_to='pins',blank=True)
	def __unicode__(self):
		return self.name

class Building(models.Model):
	DAMAGE_CHOICES = (
		('NONE','No Damage'),
		('PARTIAL','Partial Damage'),
		('DESTROYED','Destroyed')
	)
	name = models.CharField(max_length=50)
	description = models.TextField(blank=True,null=True)
	url = models.URLField(blank=True,null=True)
	coords = models.PointField(srid=theSRID,blank=True)
	model = models.FileField(upload_to='models',blank=True)
	damage = models.CharField(max_length=10, choices=DAMAGE_CHOICES,blank=True)
	buildingType = models.ForeignKey(BuildingType)
	objects = models.GeoManager()
	def getJSON(self):
		json = {}
		json['type']='Feature'
		json['geometry'] = eval(self.coords.geojson)

		#clear strange characters
		try:
			desc = str(self.description)
		except UnicodeEncodeError,e:
			import sys
			sys.stderr.write('Unicode Error'+str(e))
			desc = "unicode error"
		json['properties'] = {'name':str(self.name),'type':str(self.buildingType),'url':str(self.url),
					'description':str(desc),'damage':str(self.get_damage_display()),
					'icon':str(self.buildingType.mapPin.url)}	
		return str(json)
	def __unicode__(self):
		return self.name


class Bombing(models.Model):
	KIND_CHOICES = (
		('AERIAL','Aerial Bombardment'),
		('GROUND','Artillery Shelling'),
		('PHOSPHOROUS','White Phosphorous'),
		('DIME','Dense Inert Metal Explosive'),
		('OTHER','Other')
	)
	name = models.CharField(max_length=50)
	description = models.TextField()
	latitude = models.CharField(max_length=20) #displayed
	longitude = models.CharField(max_length=20) #displayed
	coords = models.PointField(srid=theSRID,blank=True,null=True) #hidden
	casualties = models.IntegerField(blank=True,null=True)
	time = models.DateTimeField(auto_now=False,blank=True,null=True)
	kind = models.CharField(max_length=10, choices=KIND_CHOICES)
	verified = models.BooleanField('Verified')
	
	testimony = models.ForeignKey('testimony.Text',blank=True,null=True)
	video = models.ForeignKey('testimony.Video',blank=True,null=True)
	gallery = models.ForeignKey('photologue.Gallery',blank=True,null=True)
	
	def __unicode__(self):
		return str(self.name) + " " + str(self.time.date()) + " - " + str(self.kind)

	def getJSON(self):
		json = {}
		json['type']='Feature'
		json['geometry'] = eval(self.coords.geojson)
		
		#clear strange characters
		try:
			desc = str(self.description)
		except UnicodeEncodeError,e:
			import sys
			sys.stderr.write('Unicode Error'+str(e))
			desc = "unicode error"
	#	
		json['properties'] = {'name':str(self.name),
					'description':str(desc),'casualties':str(self.casualties),
					'icon':str("%s.png" % self.kind)}	
		return str(json)
	
	def save(self):
		import geopy
		#Override default save to convert lat/lon in DMS to the right SRID
		#example input ''' 31°30'33"N   34°27'43"E '''

		self.latitude.replace(u'\xc2\xb0',' ') #clear strange characters
		self.longitude.replace(u'\xc2\xb0',' ')
		point = geopy.Point("%s %s" % (self.latitude,self.longitude)) #convert to decimal degrees
		wkt = 'POINT (%s %s)' % (point.longitude,point.latitude)
		gsm = OGRGeometry(wkt,4326) #create OGR geometry
		gsm.transform_to(SpatialReference('EPSG:%s' % theSRID)) #convert to the db srid
		self.coords = str(gsm)

		self.save_base(force_insert=False, force_update=False)
