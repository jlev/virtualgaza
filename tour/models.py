from django.contrib.gis.db import models

class Location(models.Model):
	'''The abstract base class of all geolocated models'''
	name = models.CharField(max_length=50)
	loc = models.PointField(srid=4326,blank=True) #location of rough center, for bounds
	objects = models.GeoManager()
	
	def __unicode__(self):
		return self.name
	class Meta:
		abstract = True
		#this is an abstract base class, can't be instantiated


class Neighborhood(Location):
	'''A local neighborhood, with bounds'''
	bounds = models.PolygonField(srid=4326)

class Building(Location):
	'''A building, with 3d model'''
	DAMAGE_CHOICES = (
		('NONE','No Damage'),
		('PARTIAL','Partial Damage'),
		('DESTROYED','Destroyed')
	)
	model = models.FileField(upload_to='models',blank=True)
	bounds = models.PolygonField(srid=4326,blank=True)
	damage = models.CharField(max_length=10, choices=DAMAGE_CHOICES,blank=True)

class Event(Location):
	KIND_CHOICES = (
		('AIR_BOMB','Aerial Bombing'),
		('GROUND','Ground Incursion'),
		('BUILDING','Building Destroyed'),
	)
	time = models.DateTimeField(auto_now=False)
	kind = models.CharField(max_length=10, choices=KIND_CHOICES,blank=True)
	verified = models.BooleanField('Verified')