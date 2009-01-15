from django.contrib import admin
import testimony.models

class AuthorAdmin(admin.ModelAdmin):
	fields = ['user','picture','phone_number']
	
class TextAdmin(admin.ModelAdmin):
	fieldsets = [
	    (None, {'fields': ['author','neighborhood']}),
	    ('Date', {'fields': ['created_date']}),
	    ('Content', {'fields': ['description','text']}),
		('Publication', {'fields': ['approved']}),
	]
	
class PhotoAdmin(admin.ModelAdmin):
	fieldsets = [
	    (None, {'fields': ['author']}),
	    ('Date', {'fields': ['created_date']}),
	    ('Content', {'fields': ['description','photo']}),
		('Publication', {'fields': ['approved']}),
	]
	
class VideoAdmin(admin.ModelAdmin):
	fieldsets = [
	    (None, {'fields': ['author']}),
	    ('Date', {'fields': ['created_date']}),
	    ('Content', {'fields': ['description','video']}),
		('Publication', {'fields': ['approved']}),
	]	

class AudioAdmin(admin.ModelAdmin):
	fieldsets = [
	    (None, {'fields': ['author']}),
	    ('Date', {'fields': ['created_date']}),
	    ('Content', {'fields': ['description','audio']}),
		('Publication', {'fields': ['approved']}),
	]
	
admin.site.register(testimony.models.Author, AuthorAdmin)
admin.site.register(testimony.models.Text,TextAdmin)
admin.site.register(testimony.models.Photograph,PhotoAdmin)
admin.site.register(testimony.models.Video,VideoAdmin)
admin.site.register(testimony.models.Audio,AudioAdmin)
