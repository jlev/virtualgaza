# Django settings for virtualgaza project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SEND_BROKEN_LINK_EMAILS = True

ADMINS = (
    ('Josh Levinger','jlev@mit.edu'),
)
MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Gaza'

# Default language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

from django.utils.translation import ugettext_lazy as _
LANGUAGES = (
  ('en', _('English')),
  ('ar-PS', _('Arabic')),
  ('he', _('Hebrew')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
SITE_ROOT = '/Users/jlev/Code/virtualgaza/'
MEDIA_ROOT = SITE_ROOT + 'media/'
STATIC_DOC_ROOT = MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/media/"

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'http://virtualgaza.media.mit.edu/media/admin/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware'
)

PREPEND_WWW = False  #don't want this for medialab domain

ROOT_URLCONF = 'virtualgaza.urls'

TEMPLATE_DIRS = (
	SITE_ROOT + 'templates/'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.databrowse',
    'django.contrib.gis',
    'photologue',
    'virtualgaza.tour',
    'virtualgaza.testimony',
    'django_evolution'
)

GALLERY_SAMPLE_SIZE = 4
AUTH_PROFILE_MODULE = 'testimony.UserProfile'

from settings_local import *