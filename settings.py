# Django settings for virtualgaza project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

GEOS_LIBRARY_PATH='/opt/local/lib/libgeos_c.dylib'

ADMINS = (
    ('Josh Levinger','jlev@mit.edu')
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'virtualgaza'             # Or path to database file if using sqlite3.
DATABASE_USER = 'postgres'             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

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
SITE_ROOT = '/Users/jlev/CompCult/svn/virtualgaza/'
MEDIA_ROOT = SITE_ROOT + 'media/'
STATIC_DOC_ROOT = MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''
#MEDIA_URL = 'http://www.virtualgaza.com/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = SITE_ROOT + 'media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'n^07awh1gxt@5i#ti5u(er)+(oola_97*pg9hw75!qj6=cs1zw'

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

PREPEND_WWW = False #set to true when deploying

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
    'virtualgaza.tour',
    'virtualgaza.testimony',
)

AUTH_PROFILE_MODULE = 'testimony.UserProfile'

GOOGLE_MAPS_API_KEY = 'ABQIAAAAT9uyY_WHXEyDYZHQMelCKhTpj_x8CYqdlUqSxsqEfv92evxgVhSnqavVlKF2mOnUFJZ9_YXj87jy9A'
#for virtualgaza.com