from django import forms
from tour.models import Neighborhood
from testimony.models import Author,Text,Video,Audio
from photologue.models import Photo,Gallery,GalleryUpload

from django.contrib.admin import widgets
from django.shortcuts import render_to_response
from django.template import RequestContext

class AuthorForm(forms.ModelForm):
	description_short = forms.CharField(label="About yourself in one sentence",help_text="Max length is 100 characters.")
	description = forms.CharField(label="About yourself",widget=forms.Textarea,help_text="Max length is 500 characters.",required=False)
	
	class Meta:
		model = Author
		exclude = ('date_joined','auto_approve','num_posts','last_post_time')
	
class TextForm(forms.ModelForm):
	author = forms.ModelChoiceField(queryset=Author.objects.all().order_by('last_name'))
	neighborhood = forms.ModelChoiceField(queryset=Neighborhood.objects.all().order_by('name'))
	created_date = forms.DateTimeField(label="Created",widget=widgets.AdminSplitDateTime())
	
	class Meta:
		model = Text
		exclude = ('approved','source')
	
class PhotoForm(forms.ModelForm):
	class Meta:
		model = Photo
		
class GalleryForm(forms.ModelForm):
	class Meta:
		model = Gallery

class VideoForm(forms.ModelForm):
	class Meta:
		model = Video
		
def add_author(request):
	template = "testimony/add_author.html"
	if request.method == 'POST':
		form = AuthorForm(request.POST)
		if form.is_valid():
			#fill in hidden fields
			#save password
			#email success
			form.save()
			template = "testimony/new_author.html"
	else:
		form = AuthorForm()
	return render_to_response(template,
					{"form": form},
	context_instance = RequestContext(request))

def add_text(request):
	template = "testimony/add_text.html"
	if request.method == 'POST':
		form = TextForm(request.POST)
		if form.is_valid():
			form.save()
			template = "testimony/thank_you.html"
	else:
		form = TextForm()
	return render_to_response(template,
					{"form": form},
	context_instance = RequestContext(request))