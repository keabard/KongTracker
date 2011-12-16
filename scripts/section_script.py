import sys

sys.path.append('/home/kongtracker/www/')
sys.path.append('/home/kongtracker/www/kongtracker/')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'kongtracker.settings'
from django.core.management import setup_environ
from kongtracker import settings
setup_environ(settings)

from kongtracker.kong.models import ForumSection, ForumSubSection

from BeautifulSoup import BeautifulSoup
import urllib2

url = 'http://forums.heroesofnewerth.com'
req = urllib2.Request(url)
req.add_header('User-Agent', 'Mozilla')
soup = BeautifulSoup(urllib2.urlopen(req).read())



for section_td  in soup.fetch('td', {'class' : 'alt1Active'}):
  for div_child in section_td.findChildren('div'):
    for a_child in div_child.findChildren('a'):
      if len(a_child.findChildren('strong'))>0:
        section = ForumSection.objects.create(link = 'http://forums.heroesofnewerth.com/%s'%a_child.get('href'), title = 
a_child.text)
      else:
        ForumSubSection.objects.create(link = 'http://forums.heroesofnewerth.com/%s'%a_child.get('href'), title = 
a_child.text, forum_section = section)
