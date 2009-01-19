from django.contrib.gis.db import models
from django.template.defaultfilters import slugify

theSRID = 900913

class Location(models.Model):
	name = models.CharField(max_length=100,unique=True)
	coords = models.PointField(srid=theSRID)
	objects = models.GeoManager()
	
	def getJSON(self):
		json = {}
		json['type']='Feature'
		json['geometry'] = eval(self.coords.geojson)
		json['properties'] = {'name':str(self.name),
					'link':str("/author/%s" % slugify(self.name))}
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

class Neighborhood(models.Model):
	'''A local neighborhood, with bounds'''
	name = models.CharField(max_length=50)
	bounds = models.PolygonField(srid=theSRID)
	population = models.IntegerField(blank=True,null=True)
	objects = models.GeoManager()
	
	def getJSON(self):
		json = {}
		json['type']='Feature'
		json['geometry'] = eval(self.bounds.geojson)
		pop = self.population
		if pop is None:
			pop = 0
		json['properties'] = {'name':str(self.name),'population':pop,
							'link':str("/neighborhood/%s" % slugify(self.name))}
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
	coords = models.PointField(srid=theSRID,blank=True)
	model = models.FileField(upload_to='models',blank=True)
	damage = models.CharField(max_length=10, choices=DAMAGE_CHOICES,blank=True)
	buildingType = models.ForeignKey(BuildingType)
	objects = models.GeoManager()
	
	def __unicode__(self):
		return self.name

class Event(models.Model):
	KIND_CHOICES = (
		('AIR_BOMB','Aerial Bombing'),
		('GROUND','Ground Incursion'),
		('BUILDING','Building Destroyed'),
	)
	coords = models.PointField(srid=theSRID,blank=True)
	casualties = models.IntegerField(blank=True)
	time = models.DateTimeField(auto_now=False)
	kind = models.CharField(max_length=10, choices=KIND_CHOICES,blank=True)
	verified = models.BooleanField('Verified')
	def __unicode__(self):
		return self.time + "," + self.kind