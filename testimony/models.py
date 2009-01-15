from django.db import models
from virtualgaza.tour.models import Neighborhood

class Author(models.Model):
	from django.contrib.auth.models import User
	phone_number = models.CharField(max_length=15,blank=True)
	user = models.ForeignKey(User, unique=True)
	picture = models.ImageField(upload_to='authors')
	def __unicode__(self):
		return self.user.get_full_name()

class Diary(models.Model):
	'''Abstract base class for all diary entries
	This should not be registered in the admin site, or directly exposed to users
	'''
	author = models.ForeignKey(Author) #many to one
	neighborhood = models.ForeignKey(Neighborhood,blank=True)
	created_date = models.DateTimeField("Created",auto_now=False)
	uploaded_date = models.DateTimeField("Uploaded",auto_now=True)
	description = models.CharField("Description",max_length=250)
	approved = models.BooleanField('Approved')
	
	def __unicode__(self):
		return self.description
	
	class Meta:
		abstract = True

class Text(Diary):
	text = models.TextField()
	class Meta:
		verbose_name = "diary"
		verbose_name_plural = "diaries"
	
class Photograph(Diary):
	photo = models.ImageField(upload_to='photos/%Y/%m/%d')
	class Meta:
		verbose_name_plural = "photos"

class Video(Diary):
	video = models.FileField(upload_to='video/%Y/%m/%d')
	class Meta:
		verbose_name_plural = "videos"

class Audio(Diary):
	audio = models.FileField(upload_to='audio/%Y/%m/%d')
	class Meta:
		verbose_name_plural = "audio"