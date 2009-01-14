from django.db import models
from virtualgaza.tour.models import Neighborhood

class Author(models.Model):
	from django.contrib.auth.models import User
	phone_number = models.CharField(max_length=15,blank=True)
	user = models.ForeignKey(User, unique=True)
	def __unicode__(self):
		return self.user.get_full_name()

class Testimony(models.Model):
	'''The abstract base class of all testimony models'''
	author = models.ManyToManyField(Author,verbose_name="Author")
	neighborhood = models.ManyToManyField(Neighborhood,verbose_name="Neighborhood",blank=True)
	created_date = models.DateTimeField("Created",auto_now=False)
	uploaded = models.DateTimeField("Uploaded",auto_now=True)
	description = models.CharField("Short Description",max_length=250)
	
	def __unicode__(self):
		return self.description
	
	class Meta:
		abstract = True #this is an abstract base class, can't be instantiated


class Diary(Testimony):
	text = models.TextField()
	class Meta:
		verbose_name = "diary entry"
		verbose_name_plural = "diary entries"

class Photograph(Testimony):
	photo = models.ImageField(upload_to='photos')
	class Meta:
		verbose_name_plural = "photos"

class Video(Testimony):
	video = models.FileField(upload_to='video')
	class Meta:
		verbose_name_plural = "videos"

class Audio(Testimony):
	audio = models.FileField(upload_to='audio')
	class Meta:
		verbose_name_plural = "audio"
