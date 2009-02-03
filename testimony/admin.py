from django.contrib import admin
import testimony.models

class AuthorAdmin(admin.ModelAdmin):
	list_display = ('first_name','last_name','gender','neighborhood')
	fieldsets = [
	 	('Personal', {'fields':['first_name','last_name','gender','picture']}),
		('Contact', {'fields':['email','phone_number']}),
		('Location', {'fields':['neighborhood','location']}),
	]
	
class TextAdmin(admin.ModelAdmin):
	list_display = ('author','description','created_date','uploaded_date', 'approved')
	fieldsets = [
	    (None, {'fields': ['author']}),
	    ('Date', {'fields': ['created_date']}),
	    ('Content', {'fields': ['description','text']}),
		('Publication', {'fields': ['approved']}),
	]

class VideoAdmin(admin.ModelAdmin):
	list_display = ('author','description','created_date','uploaded_date', 'approved')
	fieldsets = [
	    (None, {'fields': ['author']}),
	    ('Date', {'fields': ['created_date']}),
	    ('Content', {'fields': ['description','video','thumbnail']}),
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
	
admin.site.register(testimony.models.Author, AuthorAdmin)
admin.site.register(testimony.models.Text,TextAdmin)
admin.site.register(testimony.models.Video,VideoAdmin)
admin.site.register(testimony.models.Audio,AudioAdmin)
