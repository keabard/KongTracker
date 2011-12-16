# -*- encoding: utf-8 -*-

#-- Django imports
from django.views.generic.simple import direct_to_template
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.db.models import Max
from django.shortcuts import get_object_or_404

#-- KongTracker imports
from kong.forms import SearchForm
from kong.models import KongPost, ForumSection, ForumSubSection, KongThread

#-- Views
def index(request):
    
    nb_posts = request.GET.get('nb_posts', 10)
    latest_kong_posts = KongPost.objects.all().order_by('-date')[:nb_posts]
    
    search_form = SearchForm()
    return direct_to_template(request, 'index.html', {'forum_sections' : ForumSection.objects.order_by('title'), 
                                                                                        'latest_kong_posts' : latest_kong_posts, 
                                                                                                'search_form' : search_form, 
                                                                                                'nb_posts' : nb_posts})
    
def section_item(request, forum_section_id):
    forum_section = get_object_or_404(ForumSection, id = forum_section_id)
    subsections = forum_section.forumsubsection_set.all()
    search_form = SearchForm()
    
    kong_threads_list = forum_section.threads.order_by('-last_modified')
    
    # Show 25 kong threads per page
    paginator = Paginator(kong_threads_list, 25)

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        kong_threads = paginator.page(page)
    except (EmptyPage, InvalidPage):
        kong_threads = paginator.page(paginator.num_pages)
    
    return direct_to_template(request,  'section_item.html',  {'kong_threads' : kong_threads, 
                                                                                                    'current_forum_section' : forum_section, 
                                                                                                    'forum_sections' : ForumSection.objects.order_by('title'),
                                                                                                    'subsections' : subsections, 
                                                                                                'search_form' : search_form})
                                                                                                    
def subsection_item(request, forum_subsection_id):
    subsection = ForumSubSection.objects.get(id = forum_subsection_id)
    forum_section = subsection.forum_section
    subsections = forum_section.forumsubsection_set.all()
    kong_threads_list = subsection.threads.order_by('-last_modified')
    search_form = SearchForm()
    
    # Show 25 kong threads per page
    paginator = Paginator(kong_threads_list, 25)

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        kong_threads = paginator.page(page)
    except (EmptyPage, InvalidPage):
        kong_threads = paginator.page(paginator.num_pages)

    
    return direct_to_template(request,  'subsection_item.html',  {'kong_threads' : kong_threads,  
                                                                                                    'current_forum_section' : forum_section, 
                                                                                                    'forum_sections' : ForumSection.objects.order_by('title'),
                                                                                                    'subsections' : subsections, 
                                                                                                    'current_subsection' : subsection, 
                                                                                                'search_form' : search_form})
                                                                                                    
def thread_item(request, thread_id):
    kong_thread = KongThread.objects.get(id = thread_id)
    search_form = SearchForm()
    return direct_to_template(request, 'thread_item.html', {'kong_posts' : kong_thread.kongpost_set.order_by('date'), 
                                                                                                'forum_sections' : ForumSection.objects.order_by('title'), 
                                                                                                'current_thread' : kong_thread, 
                                                                                                'search_form' : search_form})
                                                                                                
def search_kongs(request):
    if request.method == 'GET':
        search_form = SearchForm()
        search_data = request.GET
        
        search_text = search_data.get('search_text')
        search_type = search_data.get('search_type')
        
        if search_type == 'thread':
            kong_threads_list = KongThread.objects.filter(title__icontains = search_text).order_by('-last_modified')
            
            # Show 25 kong threads per page
            paginator = Paginator(kong_threads_list, 25)

            # Make sure page request is an int. If not, deliver first page.
            try:
                page = int(request.GET.get('page', 1))
            except ValueError:
                page = 1

            # If page request (9999) is out of range, deliver last page of results.
            try:
                kong_threads = paginator.page(page)
            except (EmptyPage, InvalidPage):
                kong_threads = paginator.page(paginator.num_pages)

            
            return direct_to_template(request, 'thread_search_results.html', {'kong_threads' : kong_threads, 
                                                                                                                            'forum_sections' : ForumSection.objects.order_by('title'),
                                                                                                                            'search_text' : search_text, 
                                                                                                                            'search_type' : search_type, 
                                                                                                                            'search_form' : search_form})
        elif search_type == 'post':
            
            kong_posts_list = KongPost.objects.filter(message__icontains = search_text).order_by('-date')
            
            # Show 25 kong threads per page
            paginator = Paginator(kong_posts_list, 25)

            # Make sure page request is an int. If not, deliver first page.
            try:
                page = int(request.GET.get('page', 1))
            except ValueError:
                page = 1

            # If page request (9999) is out of range, deliver last page of results.
            try:
                kong_posts = paginator.page(page)
            except (EmptyPage, InvalidPage):
                kong_posts = paginator.page(paginator.num_pages)

            
            return direct_to_template(request, 'post_search_results.html', {'kong_posts' : kong_posts, 
                                                                                                                            'forum_sections' : ForumSection.objects.order_by('title'),
                                                                                                                            'search_text' : search_text, 
                                                                                                                            'search_type' : search_type, 
                                                                                                                            'search_form' : search_form})
        else:
            return HttpResponseRedirect(reverse('kongtracker_index'))
        
    return HttpResponse('wtf ?')
    
def suggestion(request):
    if request.method == 'GET':
        search_form = SearchForm()
        return direct_to_template(request, 'suggestion.html', {'search_form' : search_form, 
                                                                                                            'forum_sections' : ForumSection.objects.order_by('title')})
    
    else:
        return HttpResponse('wtf ?')

def s2_staff(request):
    if request.method == 'GET':
        return direct_to_template(request, 's2_staff.html', {'authors' : KongPost.objects.order_by('author').values_list('author', flat=True).distinct()})
    else:
        return HttpResponse('wtf ?')
