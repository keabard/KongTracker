#!/usr/bin/python2.6

#-- Python imports
import urllib2
import re
import BeautifulSoup

import time
import sys
import datetime
from dateutil.relativedelta import relativedelta

#-- Django script zomg
sys.path.append('/home/kongtracker/www/')
sys.path.append('/home/kongtracker/www/kongtracker/')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'kongtracker.settings'
from django.core.management import setup_environ
from kongtracker.kong.utils import get_decoded_text, get_encoded_text
from kongtracker import settings
setup_environ(settings)

#-- Django imports
from django.contrib.contenttypes.models import ContentType

#-- KongTracker imports
from kongtracker.kong.models import KongPost, KongThread, ForumSection, ForumSubSection

#-- Script arguments
if sys.argv[1] == 'create':
    SCRIPT_MODE = 'CREATE'
    KongThread.objects.all().delete()
elif sys.argv[1] == 'update':
    SCRIPT_MODE = 'UPDATE'
else:
    sys.exit('Bad arguments given, script exit. Try "create" or "update".')

#-- Functions

def uniform_date(original_date):
    today_struct = time.gmtime()
    today_utc = datetime.datetime(year = today_struct.tm_year,
                                  month = today_struct.tm_mon,
				  day = today_struct.tm_mday,
				  hour = today_struct.tm_hour,
				  minute = today_struct.tm_min)
    if 'Yesterday' in original_date:
        yesterday = today_utc - relativedelta(days = 1)
        return original_date.replace('Yesterday', yesterday.strftime('%m-%d-%Y'))
    elif 'Today' in original_date:
        return original_date.replace('Today', today_utc.strftime('%m-%d-%Y'))
    else:
        return original_date

def get_kongs_urls(soup, section_or_subsection):
    # Get a list of (topic_url) of each topic that is marked with a kong
    kongs_list = []
    if SCRIPT_MODE == 'UPDATE':
        for kong_img in soup.fetch('img', {'src' : 'images/misc/stafftracker.png' }):
        
            # Get latest post time of this kong_thread
            thread_last_post_time = kong_img.findParent('tr').findChild('span', {'class' : 'time'}).findParent('div').text
            stripped_last_post_time = re.findall('(.*?..:.. .M)', thread_last_post_time)[0]
            last_post_time = uniform_date(stripped_last_post_time)
            last_post_datetime = datetime.datetime.strptime(last_post_time, '%m-%d-%Y%I:%M %p')
            
            # Check if the kong_thread is a Sticky
            if len(kong_img.findParent('div').findChildren('img',  alt='Sticky Thread')) > 0:
                is_sticky = True
            else:
                is_sticky = False
                
            # Check the number of kong_posts in this kong_thread
            kong_thread_title = kong_img.findParent('tr').fetch('a', {'id' : re.compile('thread_title_.*?')})[0].text
            kong_thread_id = int(re.findall('.*?p=(.*?)#post', kong_img.findParent('a')['href'])[0])

            if KongThread.objects.filter(thread_id = kong_thread_id, 
                                                        title__contains = kong_thread_title).count() == 1:
                kong_thread = KongThread.objects.get(thread_id = kong_thread_id, 
                                                        title__contains = kong_thread_title)
                kong_posts_number = int(re.findall('(.*?) Staff Post...', kong_img['alt'])[0])
                # If there are less or equal number of kong posts in this kong thread, ignore it
                if kong_posts_number <= KongThread.objects.get(thread_id = kong_thread_id, 
                                                                                                title__contains = kong_thread_title).kongpost_set.count():
		    try:
	                    print get_decoded_text(u'Nothing new on thread %s !'%get_decoded_text(kong_thread_title))
		    except:
                            print "******* Uh oh, can't write the thread title down :("
                    
                    if section_or_subsection.threads.count() and \
                    last_post_datetime < section_or_subsection.threads.filter(last_modified__isnull = False).latest('last_modified').last_modified and \
                    not is_sticky:
                        kongs_list.append('STOP')
                        break
                
                else:
                    kongs_list.append(kong_img.findParent('a')['href'])
            else:
                kongs_list.append(kong_img.findParent('a')['href'])
        else:
            
            # Get latest post time of first thread in this section page
            # if there is any thread on this page...
            page_threads = soup.fetch('td', {'id' : re.compile("td_threadtitle_.*?")})
            if len(page_threads) > 0 and not page_threads[0].findParent('tr').findChild('span', {'class' : 'time'}) == None:
                thread_last_post_time = page_threads[0].findParent('tr').findChild('span', {'class' : 'time'}).findParent('div').text
                stripped_last_post_time = re.findall('(.*?..:.. .M)', thread_last_post_time)[0]
                last_post_time = uniform_date(stripped_last_post_time)
                last_post_datetime = datetime.datetime.strptime(last_post_time, '%m-%d-%Y%I:%M %p')
                
                # Check if the first thread is a Sticky
                if len(page_threads[0].findParent('tr').findChildren('img', alt='Sticky Thread')) > 0:
                    is_sticky = True
                else:
                    is_sticky = False
                
		# If the last post of the first thread is older than our last kong for this section/subsection, just stop
                if section_or_subsection.threads.count() and \
                last_post_datetime < section_or_subsection.threads.filter(last_modified__isnull = False).latest('last_modified').last_modified and \
                not is_sticky:
                    kongs_list.append('STOP')

		# If the last post of the first thread is older than one week, just stop
                if last_post_datetime < datetime.datetime.now() - relativedelta(weeks = 1):
                    kongs_list.append('STOP')
            
    elif SCRIPT_MODE == 'CREATE':
        for kong_img in soup.fetch('img', {'src' : 'images/misc/stafftracker.png' }):
            kongs_list.append(kong_img.findParent('a')['href'])
    
	
    return kongs_list
	

def get_page_numbers(soup):
    # Get the max number of pages on a forum section
    if len(soup.fetch(title=re.compile('Last Page - Results.*'))) == 0:
        if len(soup.fetch('div', {'class' : 'pagenav'})) == 0:
            return 1
        else:
            return int(soup.fetch('div', {'class' : 'pagenav'})[0].findChildren('td')[-2].text)
    else:
        return int(soup.fetch(title=re.compile('Last Page - Results.*'))[0]['href'].split('page=')[1])

def print_kongs_per_page(giant_kong_dict):
    # Given the giant_kong_dict, print the number of kongs for each page
    for j in range(10):
        print "Page %s : %s Kongs"%(j+1, len(giant_kong_dict[j+1]))

def fetch_kong_posts(kong_post_url, forum_section):
    # Given a particular first_kong_post_url, get the HTMLSource and retrieve the other kong posts!

    print 'KONG_POST_URL : %s'%kong_post_url

    # Prepare request and launch it
    kong_post_req = urllib2.Request(kong_post_url)
    kong_post_req.add_header('User-Agent', 'Mozilla 5.0')
    kong_post_string = ''
    while not kong_post_string:
        try:
            kong_post_string = urllib2.urlopen(kong_post_req).read()
        except:
            print "******* Error while fetching kong_post_string! Let's get it again ! ********"
    
    kong_thread_id = re.findall('.php\?p=(.*?)#post', kong_post_url)[0]
    
    # if id doesnt exist, RETURN
    if not kong_thread_id:
        return
        
    kong_thread_url = kong_post_url.split('#post')[0]
    
    # Build a beautiful soup with the HTML Source
    soup = BeautifulSoup.BeautifulSoup(kong_post_string)
    
    # Create or retrieve kong thread
    kong_thread, created = KongThread.objects.get_or_create(thread_id = int(kong_thread_id), 
                                                                                        object_id = forum_section.id, 
                                                                                        content_type = ContentType.objects.get_for_model(forum_section), 
                                                                                        link = kong_thread_url, 
                                                                                        title = soup.fetch('td', 'navbar')[0].text
                                                                                        )
                                                                                        
    if created :
        try:
            print 'New Kong Thread created ! %s - %s'%(kong_thread.title,  kong_thread.id)
        except:
            print 'New Kong Thread created ! ID : %s but couldnt write its title :('%kong_thread.id

    # Get the kong_post !
    while True:
        
        kong_post_id = kong_post_url.split('#post')[1]
        
        # if id doesnt exist, BREAK
        if not kong_post_id:
            break
        kong_post_tables = soup.fetch('table', id='post%s'%kong_post_id)
        if len(kong_post_tables) == 0:
            break
        else:
            kong_post_table = kong_post_tables[0]
    
        post_date_td = kong_post_table.fetch('td', {'class' : 'thead'})[0]
                
        post_date = re.findall('date(.*?, ..:.. .M)', post_date_td.text)[0]
        
        post_div = kong_post_table.fetch('div',  {'id' : 'postmenu_%s'%kong_post_id})[0]
        temp_datetime = uniform_date(post_date)
        post_datetime = datetime.datetime.strptime(temp_datetime, '%m-%d-%Y, %I:%M %p')

	post_author = post_div.fetch('a')[0].text
	if 'formatting' in post_author:
		post_author_bis = post_author
		post_author = re.findall('Username formatting(.*?)/Username formatting', post_author_bis)[0]

		# Create a kong post and fill in its attributes
        already_created = KongPost.objects.filter(author = post_author,
                                                                    forum_id = kong_post_id, 
                                                                    date = post_datetime , 
                                                                    kong_thread = kong_thread,  
                                                                    link = kong_post_url).count() > 0

        if not already_created:
            kong_post = KongPost.objects.create(author = post_author,
                                                                    forum_id = kong_post_id, 
                                                                    date = post_datetime , 
                                                                    kong_thread = kong_thread,  
                                                                    link = kong_post_url, 
                                                                    message = kong_post_table.fetch('div', id='post_message_%s'%kong_post_id)[0])
            try :
                print 'New KongPost created ! topic : %s %s - id : %s'%(get_decoded_text(kong_thread.title), post_datetime.strftime('%d/%m/%Y %H:%M'), kong_post.id)
            except :
                print "New KongPost created but can't write its title :("
            kong_thread.last_modified = post_datetime
            kong_thread.save()
        else:
            try :
                print 'KongPost already exist on topic %s !'%get_decoded_text(kong_thread.title)
            except :
                print "KongPost already exist on topic, but can't write topic title :("
        
        # If there is a next kong post, here we go again ! or not :(
        next_kong_post_imgs = kong_post_table.fetch('img', alt='Click here to go to the next staff post in this thread.')		
        if len(next_kong_post_imgs) == 0:
            break
        else:
            next_kong_post_url = next_kong_post_imgs[0].findParent('a')['href']
            print 'NEXT KONG POST URL : %s'%next_kong_post_url
            # Check for kong post loops
            if next_kong_post_url in kong_post_url:
                return
            # If the link redirects to a new thread
            if 'showthread' in next_kong_post_url:
                kong_post_url = kong_post_url.split('showthread')[0] + next_kong_post_url
#                kong_thread_url = kong_post_url.split('#post')[0]
                new_req = urllib2.Request(kong_post_url)
                new_req.add_header('User-Agent', 'Mozilla 5.0')
                soup = ''
                while not soup:
                    try:
                        soup = BeautifulSoup.BeautifulSoup(urllib2.urlopen(new_req).read())
                    except:
                        print "*** Erreur en demandant la soupe ! ***"
            else:
                kong_post_url = kong_post_url.split('#')[0]+'#'+next_kong_post_url.split('#')[1]
            print "NEW KONG POST URL : %s"%kong_post_url
            
def delete_empty_threads():
    KongThread.objects.filter(kongpost__isnull = True).delete()

#-- End : Functions

page_number_arguments = '&order=desc&page=%s'
forum_url = 'http://forums.heroesofnewerth.com/'

sections_and_subsections = list(ForumSection.objects.all())
sections_and_subsections.extend(list(ForumSubSection.objects.all()))

for forum_section in sections_and_subsections:
    section_req = urllib2.Request(forum_section.link)
    section_req.add_header('User-Agent', 'Mozilla 5.0')
    print 'Forum section %s'%forum_section.title
    section_soup = ''
    while not section_soup:
        try:
            section_soup = BeautifulSoup.BeautifulSoup(urllib2.urlopen(section_req).read())
        except:
            print "*** Erreur en demandant la section_soup ***"
    pages_number = get_page_numbers(section_soup)
    print 'Number of pages : %s'%pages_number

    for i in range(pages_number):
        kong_post_url = ''
        print 'Processing page %s of forum section : %s'%(i+1, forum_section.title)
        page_req = urllib2.Request(forum_section.link+page_number_arguments%(i+1))
        page_req.add_header('User-Agent', 'Mozilla 5.0')
        page_soup = ''
        while not page_soup:
            try:
                page_soup = BeautifulSoup.BeautifulSoup(urllib2.urlopen(page_req).read())
            except:
                print "*** Erreur en demandant la page_soup ***"
        
        kong_post_urls = get_kongs_urls(page_soup, forum_section)
        print 'On page %s, kong_post_urls : %s'%(i+1, len(kong_post_urls))
        for kong_post_url in kong_post_urls:
            if kong_post_url == 'STOP':
                break
            fetch_kong_posts(forum_url+kong_post_url, forum_section)
        
        if kong_post_url == 'STOP':
            break

delete_empty_threads()





	


