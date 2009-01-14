from django.contrib import admin
import testimony.models

class AuthorAdmin(admin.ModelAdmin):
	pass
	
class DiaryAdmin(admin.ModelAdmin):
	pass
	
admin.site.register(testimony.models.Author, AuthorAdmin)
admin.site.register(testimony.models.Diary)
admin.site.register(testimony.models.Video)
admin.site.register(testimony.models.Audio)
