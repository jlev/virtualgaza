from django.core.management import setup_environ
import settings
setup_environ(settings)

from testimony.models import Text,Author
import feedcache
import shelve
import urllib2
from BeautifulSoup import BeautifulSoup,HTMLParser
import datetime

feeds = ["http://gazaeng.blogspot.com/feeds/posts/default"]

def update():
	storage = shelve.open('.feedcache',writeback=True)
	try:
		cache = feedcache.Cache(storage)
		for f in feeds:
			parsed_data = cache.fetch(f)
			print f,"has",len(parsed_data.entries),"entries"
			
			for e in parsed_data.entries:
				try:
					if e.read:
						#print "already read"
						continue
				except AttributeError,err:
					#haven't marked the entry yet, ignore
					#print err
					pass
						
				t = Text()
				t.title = e.title
				t.created_date = datetime.datetime(*e.published_parsed[:7])
				#convert from dict to datetime object for django storage
				
				#respect description max_length
				desc = e.subtitle
				max_length = 250
				if len(desc) > max_length:
					desc = desc[:(max_length-3)] + '...'
				t.description = desc
	
				#find link to full story in soup
				#assumes it is the only link
				descSoup = BeautifulSoup(e.subtitle)
				theLink = descSoup.a
				if theLink is not None:
					t.source = theLink['href']
				else:
					#no link
					e.read = True
					continue
	
				print "loading",t.source
				try:
					sourcePage = urllib2.urlopen(t.source)
				except urllib2.URLError,err:
					print err
					e.read = True
					continue
				if sourcePage.info().getheader('Content-Type') != "text/html":
					print sourcePage.url,"is not html, skipping"
					e.read = True
					continue

				#got a page, check for known sources
				if sourcePage.url.count('btselem.org') > 0:
					print "parsing",sourcePage.url
					sourceSoup = BeautifulSoup(sourcePage)
					#B'Tselem content in <p class="runing-text">
					contentList = sourceSoup.findAll('p',attrs={"class":"runing-text"})
					content = ""
					for p in contentList:
						if p.string is not None:
							content += str(p.string)
							content += "\n"
					t.text = content
					t.author = Author.objects.filter(first_name__iexact="BTselem")[0]
						#there can be only one
					
#		works, but not yet authorized
#				elif sourcePage.url.count('hamoked.org.il') > 0:
#					print "parsing",sourcePage.url
#					sourceSoup = BeautifulSoup(sourcePage)
#					contentList = sourceSoup.findAll('p',attrs={"class":"MsoNormal"})
#					content = ""
#					for p in contentList:
#						if p.string is not None:
#							content += str(p.string)
#							content += "\n"
#					t.text = content
#					t.author = Author.objects.filter(first_name__iexact="Hamoked")[0]			
				else:
					print "unrecognized author:",sourcePage.url
					e.read = True
					continue
				
				t.save()
				e.read = True
	finally:
		storage.close()
		print "done"
	return

if __name__ == "__main__":
	update()