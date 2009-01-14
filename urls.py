from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib import databrowse
from django.contrib.auth.decorators import login_required
from virtualgaza.testimony.models import Diary,Video,Audio,Photograph
from virtualgaza.tour.models import Neighborhood,Building,Event

admin.autodiscover()

databrowse.site.register(Diary)
databrowse.site.register(Video)
databrowse.site.register(Audio)
databrowse.site.register(Photograph)

databrowse.site.register(Neighborhood)
databrowse.site.register(Building)
databrowse.site.register(Event)

urlpatterns = patterns('',
	(r'^admin/(.*)', admin.site.root),
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	(r'^db/(.*)', login_required(databrowse.site.root)),
	(r'^accounts/login/$', 'django.contrib.auth.views.login'),
)

info_dict = {
    'queryset': Diary.objects.all(),
    'date_field': 'created_date',
}

urlpatterns += patterns('django.views.generic.date_based',
   (r'^diary/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$', 'object_detail', info_dict),
   (r'^diary/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',               'archive_day',   info_dict),
   (r'^diary/(?P<year>\d{4})/(?P<month>[a-z]{3})/$',                                'archive_month', info_dict),
   (r'^diary/(?P<year>\d{4})/$',                                                    'archive_year',  info_dict),
)
 
#urlpatterns += patterns('virtualgaza.tour.views',
#	(r'^neighborhood/<name>',neighborhoods),
#	(r'^buildings/<name>',building),
#	(r'^events/(?P<year>\d{4})/$',event_year),
#	(r'^events/(?P<year>\d{4})/(?P<month>\d{2})/$',event_month),
#	(r'^events/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d+)/$',event_day),
#)