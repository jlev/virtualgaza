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

databrowse.site.register(virtualgaza.testimony.models.Author)
databrowse.site.register(virtualgaza.testimony.models.Text)
databrowse.site.register(virtualgaza.testimony.models.Video)
databrowse.site.register(virtualgaza.testimony.models.Audio)
databrowse.site.register(virtualgaza.testimony.models.PhotoAlbum)
databrowse.site.register(virtualgaza.testimony.models.Photograph)

databrowse.site.register(virtualgaza.tour.models.Neighborhood)
databrowse.site.register(virtualgaza.tour.models.Building)
databrowse.site.register(virtualgaza.tour.models.Event)

#MAP URLS
urlpatterns = patterns('virtualgaza.tour.views',
	(r'^$','all_neighborhoods'),
	(r'^neighborhood/$','all_neighborhoods'),
	(r'^neighborhood/(?P<nameSlug>[\w-]+)/$','one_neighborhood'),
)

#AUTHOR URLS
urlpatterns += patterns('virtualgaza.testimony.views',
	(r'^recent/$','posts_by_recent',{'num_latest':10}),
	(r'^author/$','authors_by_neighborhood'),
	(r'^author/(?P<id>)/$','author_by_id'),
	(r'^author/(?P<firstName>[\w-]+)_(?P<lastName>[\w-]+)/$','author_by_full_name'),
	(r'^author/(?P<firstName>[\w-]+)_(?P<lastName>[\w-]+)/(?P<year>\d{4})/$', 'posts_by_author_and_year'),
	(r'^author/(?P<firstName>[\w-]+)_(?P<lastName>[\w-]+)/(?P<year>\d{4})/(?P<month>\w{1,2})/$', 'posts_by_author_and_month'),
	(r'^author/(?P<firstName>[\w-]+)_(?P<lastName>[\w-]+)/(?P<year>\d{4})/(?P<month>\w{1,2})/(?P<day>\w{1,2})/$', 'posts_by_author_and_date'),
	(r'^search/$','search_for_author'),
)

#ADMIN URLS
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