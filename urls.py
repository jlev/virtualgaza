from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib import databrowse
from django.contrib.auth.decorators import login_required
from virtualgaza.testimony.models import Text,Video,Audio,Photograph
from virtualgaza.tour.models import Neighborhood,Building,Event

admin.autodiscover()

databrowse.site.register(Text)
databrowse.site.register(Video)
databrowse.site.register(Audio)
databrowse.site.register(Photograph)

databrowse.site.register(Neighborhood)
databrowse.site.register(Building)
databrowse.site.register(Event)

urlpatterns = patterns('',
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	(r'^admin/(.*)', admin.site.root),
	(r'^db/(.*)', login_required(databrowse.site.root)),
	(r'^accounts/login/$', 'django.contrib.auth.views.login'),
)

text_info_dict = {
    'queryset': Text.objects.all(),
    'date_field': 'created_date',
}

urlpatterns += patterns('django.views.generic.date_based',
   (r'^diary/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$', 'object_detail', text_info_dict),
   (r'^diary/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',               'archive_day',   text_info_dict),
   (r'^diary/(?P<year>\d{4})/(?P<month>[a-z]{3})/$',                                'archive_month', text_info_dict),
   (r'^diary/(?P<year>\d{4})/$',                                                    'archive_year',  text_info_dict),
)


#urlpatterns += patterns('virtualgaza.tour.views',
#	(r'^neighborhood/<name>',neighborhoods),
#	(r'^buildings/<name>',building),
#	(r'^events/(?P<year>\d{4})/$',event_year),
#	(r'^events/(?P<year>\d{4})/(?P<month>\d{2})/$',event_month),
#	(r'^events/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d+)/$',event_day),
#)

#let django serve the static media when in debug mode
if settings.DEBUG:
	urlpatterns += patterns('',
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
	)