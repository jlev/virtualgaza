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

databrowse.site.register(virtualgaza.tour.models.Neighborhood)
databrowse.site.register(virtualgaza.tour.models.Building)
databrowse.site.register(virtualgaza.tour.models.Bombing)

#MAP URLS
urlpatterns = patterns('virtualgaza.tour.views',
	(r'^$','frontpage'),
	(r'^ajax/neighborhoods_within_bounds/$','neighborhoods_within_bounds'),
	(r'^neighborhood/(?P<nameSlug>[\w-]+)/$','neighborhood_page'),
)

#AUTHOR URLS
urlpatterns += patterns('virtualgaza.testimony.views',
	(r'^recent/$','posts_by_recent',{'num_latest':25}),
	(r'^testimony/$','all_posts'),
	(r'^author/$','authors_by_neighborhood'),
	(r'^author/(?P<firstName>[A-Za-z-]+)/$','author_by_one_name'),
	(r'^author/(?P<firstName>[\w-]+)_(?P<lastName>[\w-]+)/$','author_by_full_name'),
	(r'^author/(?P<firstName>[\w-]+)_(?P<lastName>[\w-]+)/(?P<year>\d{4})/$', 'posts_by_author_and_year'),
	(r'^author/(?P<firstName>[\w-]+)_(?P<lastName>[\w-]+)/(?P<year>\d{4})/(?P<month>\w{1,2})/$', 'posts_by_author_and_month'),
	(r'^author/(?P<firstName>[\w-]+)_(?P<lastName>[\w-]+)/(?P<year>\d{4})/(?P<month>\w{1,2})/(?P<day>\w{1,2})/$', 'posts_by_author_and_date'),
	(r'^search/$','search'),
)

#PHOTO URLS
urlpatterns += patterns('',
	(r'^photologue/', include('photologue.urls')),
)

#VIDEO URLS
urlpatterns += patterns('virtualgaza.testimony.views',
	(r'^video/recent/$', 'recent_videos'),
	(r'^video/$', 'all_videos'),
	(r'^video/(?P<year>\d{4})/(?P<month>\w{1,2})/(?P<day>\w{1,2})/$', 'video_by_date'),
)

#FORM URLS
urlpatterns += patterns('virtualgaza.testimony.forms',
	(r'^submit/text/$','add_text'),
	(r'^submit/author/$','add_author'),
)

#ADMIN URLS
urlpatterns += patterns('',
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	(r'^admin/(.*)', admin.site.root),
	(r'^admin/jsi18n', 'django.views.i18n.javascript_catalog'),
	(r'^db/(.*)', login_required(databrowse.site.root)),
	(r'^accounts/login/$', 'django.contrib.auth.views.login'),
	(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': settings.MEDIA_URL + 'favicon.ico'}),
	(r'robots.txt$','django.views.generic.simple.redirect_to', {'url': settings.MEDIA_URL + 'robots.txt'}),
	(r'proxy/(?P<theURL>.*)$','virtualgaza.views.proxy'),
)


#let django serve the static media when in debug mode
if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
	)