# coding=utf8
#for the unicode strings in Bombing.save()

from django.contrib.gis.db import models
from django.template.defaultfilters import slugify
from django.contrib.gis.gdal import SpatialReference,OGRGeometry

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
		json['properties'] = {'name':str(self.name),'displayName':str(firstName + " " + lastName),
					'link':str("/author/%s/" % slugify(self.name))}	
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
	coords = models.PointField(srid=theSRID,blank=True)
	model = models.FileField(upload_to='models',blank=True)
	damage = models.CharField(max_length=10, choices=DAMAGE_CHOICES,blank=True)
	buildingType = models.ForeignKey(BuildingType)
	objects = models.GeoManager()
	
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
	name = models.CharField(max_length=25)
	description = models.TextField()
	latitude = models.CharField(max_length=20) #displayed
	longitude = models.CharField(max_length=20) #displayed
	coords = models.PointField(srid=theSRID,blank=True,null=True) #hidden
	casualties = models.IntegerField(blank=True,null=True)	
	time = models.DateTimeField(auto_now=False,blank=True)
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
		json['properties'] = {'name':str(self.name),'displayName':str(self.name),
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