from django.db import models
import datetime
from django.template.defaultfilters import slugify

GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

class Author(models.Model):
	first_name = models.CharField('first name', max_length=30, blank=True)
	last_name = models.CharField('last name', max_length=30, blank=True)
	gender = models.CharField('gender',max_length=1, choices = GENDER_CHOICES,blank=True)
	age = models.IntegerField('age',default=0,blank=True)
	email = models.EmailField('e-mail address', blank=True)
	date_joined = models.DateTimeField('date joined', default=datetime.datetime.now)
	phone_number = models.CharField(max_length=15,blank=True)
	picture = models.ForeignKey('photologue.Photo',null=True,blank=True)
	neighborhood = models.ForeignKey('tour.Neighborhood')
	num_posts = models.IntegerField(default=0)
	last_post_time = models.DateTimeField('last post',null=True,blank=True)
	auto_approve = models.BooleanField("Auto Approve",
		default=False,help_text="Make sure this author is trusted before enabling.")
	description = models.CharField("Brief Author Biography",max_length=500,null=True,blank=True)
	description_short = models.CharField("One Sentance Bio",max_length=100,null=True,blank=True)
	
	def get_full_name(self):
		full_name = u'%s %s' % (self.first_name, self.last_name)
		return full_name.strip()
		
	def increase_postcount(self):
		self.num_posts += 1
	
	def set_last_post_time(self):
		self.last_post_time = datetime.datetime.now()
		
	def __unicode__(self):
		return self.get_full_name()

class Diary(models.Model):
	'''Abstract base class for all diary entries
	This should not be registered in the admin site or directly exposed to users
	'''
	author = models.ForeignKey(Author)
	created_date = models.DateTimeField("Created",auto_now=False)
	uploaded_date = models.DateTimeField("Uploaded",auto_now=True)
	description = models.CharField("Description",max_length=250)
	approved = models.BooleanField('Approved',default=False)
	source = models.CharField("Content Source",max_length=200,null=True,blank=True,help_text="Where did this content come from? Will be displayed on post page, so links allowed.")
	
	def __unicode__(self):
		return self.description
	
	def save(self):
		self.author.increase_postcount()
		if self.author.auto_approve:
			approved = True
		self.save_base(force_insert=False, force_update=False)
	
	class Meta:
		abstract = True

class Text(Diary):
	text = models.TextField()
	class Meta:
		verbose_name = "text"
		verbose_name_plural = "texts"

class Video(Diary):
	video = models.FileField(upload_to='video/%Y/%m/%d')
	class Meta:
		verbose_name_plural = "videos"
	def save(self):
		#TODO: convert to flv
		#generate thumbnail
		import os
		cmd = "ffmpeg  -itsoffset -10 -y -i %s -vcodec mjpeg -vframes 1 -an -f rawvideo -s 100x100 %s" % (self.video.path,self.video.path + ".jpg")
		os.popen(cmd)
		self.save_base(force_insert=False, force_update=False)

class Audio(Diary):
	audio = models.FileField(upload_to='audio/%Y/%m/%d')
	class Meta:
		verbose_name_plural = "audio"
		
class Feed(models.Model):
	title = models.CharField("Feed Title",max_length=100)
	url = models.URLField("Feed URL")
	regex = models.CharField("RegEx Filter on Entry Titles",max_length=200,blank=True)
	default_author = models.ForeignKey(Author,blank=True,null=True)
	
	def __unicode__(self):
		return self.title