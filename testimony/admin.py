from django.contrib import admin
import django.forms as forms
from testimony.models import *

class AuthorForm(forms.ModelForm):
	description = forms.CharField(label="Brief Author Biography",widget=forms.Textarea,help_text="Max length is 500 characters.",required=False)
	class Meta:
		model = Author

class AuthorAdmin(admin.ModelAdmin):
	list_display = ('first_name','last_name','gender','neighborhood')
	fieldsets = [
	 	('Personal', {'fields':['first_name','last_name','gender','picture','auto_approve','description','description_short']}),
		('Contact', {'fields':['email','phone_number']}),
		('Location', {'fields':['neighborhood']}),
	]
	form = AuthorForm
	
class TextAdmin(admin.ModelAdmin):
	list_display = ('author','neighborhood','description','created_date','uploaded_date', 'approved')
	fieldsets = [
	    (None, {'fields': ['author','neighborhood']}),
	    ('Date', {'fields': ['created_date']}),
	    ('Content', {'fields': ['description','text']}),
		('Publication', {'fields': ['approved']}),
	]

class VideoAdmin(admin.ModelAdmin):
	list_display = ('author','neighborhood','description','created_date','uploaded_date', 'approved')
	fieldsets = [
	    (None, {'fields': ['author','neighborhood']}),
	    ('Date', {'fields': ['created_date']}),
	    ('Content', {'fields': ['description','video']}),
		('Publication', {'fields': ['approved']}),
	]	

class AudioAdmin(admin.ModelAdmin):
	list_display = ('author','description','created_date','uploaded_date', 'approved')
	fieldsets = [
	    (None, {'fields': ['author']}),
	    ('Date', {'fields': ['created_date']}),
	    ('Content', {'fields': ['description','audio']}),
		('Publication', {'fields': ['approved']}),
	]

class FeedAdmin(admin.ModelAdmin):
	fields = ['title','url','regex','default_author']
	
admin.site.register(Author, AuthorAdmin)
admin.site.register(Text,TextAdmin)
admin.site.register(Video,VideoAdmin)
admin.site.register(Audio,AudioAdmin)
admin.site.register(Feed,FeedAdmin)
