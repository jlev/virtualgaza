from django.db import models
import datetime
from django.template.defaultfilters import slugify
from virtualgaza.tour.models import Neighborhood,Location

GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

class Author(models.Model):
	#from django.contrib.auth.models import User
	#user = models.ForeignKey(User, unique=True)
	#don't use django user model on first go round
	first_name = models.CharField('first name', max_length=30, blank=True)
	last_name = models.CharField('last name', max_length=30, blank=True)
	gender = models.CharField('gender',max_length=1, choices = GENDER_CHOICES,blank=True)
	age = models.IntegerField('age',default=0,blank=True)
	email = models.EmailField('e-mail address', blank=True)
	date_joined = models.DateTimeField('date joined', default=datetime.datetime.now)
	phone_number = models.CharField(max_length=15,blank=True)
	picture = models.ImageField(upload_to='authors',blank=True)
	neighborhood = models.ForeignKey(Neighborhood)
	location = models.ForeignKey(Location,blank=True,null=True)
		#only blank or null on first creation, but save method creates proper object
	num_posts = models.IntegerField(default=0)
	last_post_time = models.DateTimeField('last post',null=True,blank=True)
	
	def get_full_name(self):
		full_name = u'%s %s' % (self.first_name, self.last_name)
		return full_name.strip()
		
	def increase_postcount(self):
		self.num_posts += 1
	
	def set_last_post_time(self):
		self.last_post_time = datetime.datetime.now()
		
	def __unicode__(self):
		return self.get_full_name()
		
	def save(self):
		if (not self.location):
			self.location = self.neighborhood.getRandomLocationWithin(
					slugify(self.first_name) + "_" + slugify(self.last_name))
		#should call super.save(), but didn't seem to work...
		self.save_base(force_insert=False, force_update=False)

class Diary(models.Model):
	'''Abstract base class for all diary entries
	This should not be registered in the admin site or directly exposed to users
	'''
	author = models.ForeignKey(Author) #many to one
	created_date = models.DateTimeField("Created",auto_now=False)
	uploaded_date = models.DateTimeField("Uploaded",auto_now=True)
	description = models.CharField("Description",max_length=250)
	approved = models.BooleanField('Approved')
	
	def __unicode__(self):
		return self.description
	
	def save(self):
		self.author.increase_postcount()
		#super.save()
		self.save_base(force_insert=False, force_update=False)
	
	class Meta:
		abstract = True

class Text(Diary):
	text = models.TextField()
	class Meta:
		verbose_name = "diary"
		verbose_name_plural = "diaries"

class Video(Diary):
	video = models.FileField(upload_to='video/%Y/%m/%d')
	class Meta:
		verbose_name_plural = "videos"

class Audio(Diary):
	audio = models.FileField(upload_to='audio/%Y/%m/%d')
	class Meta:
		verbose_name_plural = "audio"