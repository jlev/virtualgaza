from django.contrib.gis.db import models

class Neighborhood(models.Model):
	'''A local neighborhood, with bounds'''
	name = models.CharField(max_length=50)
	bounds = models.PolygonField(srid=4326)
	population = models.IntegerField(blank=True)
	objects = models.GeoManager()
	
	def __unicode__(self):
		return self.name

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
	location = models.PointField(srid=4326,blank=True)
	model = models.FileField(upload_to='models',blank=True)
	damage = models.CharField(max_length=10, choices=DAMAGE_CHOICES,blank=True)
	buildingType = models.ForeignKey(BuildingType)
	objects = models.GeoManager() #use the geographic manager
	
	def __unicode__(self):
		return self.name

class Event(models.Model):
	KIND_CHOICES = (
		('AIR_BOMB','Aerial Bombing'),
		('GROUND','Ground Incursion'),
		('BUILDING','Building Destroyed'),
	)
	location = models.PointField(srid=4326,blank=True)
	casualties = models.IntegerField(blank=True)
	time = models.DateTimeField(auto_now=False)
	kind = models.CharField(max_length=10, choices=KIND_CHOICES,blank=True)
	verified = models.BooleanField('Verified')
	def __unicode__(self):
		return self.time + "," + self.kind