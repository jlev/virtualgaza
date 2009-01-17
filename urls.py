from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib import databrowse
from django.contrib.auth.decorators import login_required

import virtualgaza.testimony.models
import virtualgaza.testimony.views
import virtualgaza.tour.models
import virtualgaza.tour.views

admin.autodiscover()

databrowse.site.register(virtualgaza.testimony.models.Text)
databrowse.site.register(virtualgaza.testimony.models.Video)
databrowse.site.register(virtualgaza.testimony.models.Audio)
databrowse.site.register(virtualgaza.testimony.models.PhotoAlbum)
databrowse.site.register(virtualgaza.testimony.models.Photograph)

databrowse.site.register(virtualgaza.tour.models.Neighborhood)
databrowse.site.register(virtualgaza.tour.models.Building)
databrowse.site.register(virtualgaza.tour.models.Event)


#need to fix these regex so they're smarter
#right now, order matters!
urlpatterns = patterns('virtualgaza.testimony.views',
	(r'^$', 'index'),
	(r'^author/$','all_authors'),
	(r'^author/(?P<id>)/$','author_by_id'),
	(r'^author/(?P<firstName>[-\w]+)-(?P<lastName>[-\w]+)/$','author_by_full_name'),
	(r'^author/(?P<lastName>[A-Za-z]+)/$','author_by_last_name'),
)

text_info_dict = {
	'queryset': virtualgaza.testimony.models.Text.objects.filter(approved=1),
	'date_field': 'created_date'
}
urlpatterns += patterns('django.views.generic.date_based',
	(r'^testimony/(?P<year>\d{4})/(?P<month>\w{1,2})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$', 'object_detail',
		dict(text_info_dict,month_format='%m',slug_field='description')), #add slug field only for object_detail
	(r'^testimony/(?P<year>\d{4})/(?P<month>\w{1,2})/(?P<day>\w{1,2})/$','archive_day',
		dict(text_info_dict,month_format='%m')),
	(r'^testimony/(?P<year>\d{4})/(?P<month>\w{1,2})/$','archive_month',
		dict(text_info_dict,month_format='%m')),
	(r'^testimony/(?P<year>\d{4})/$','archive_year',text_info_dict),
	(r'^testimony/$','archive_index',
		dict(text_info_dict,num_latest=10)),
)

urlpatterns += patterns('',
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	(r'^admin/(.*)', admin.site.root),
	(r'^db/(.*)', login_required(databrowse.site.root)),
	(r'^accounts/login/$', 'django.contrib.auth.views.login'),
)


#let django serve the static media when in debug mode
if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
	)