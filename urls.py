from django.conf.urls.defaults import *
from django.conf import settings

from kong.views import index, section_item, subsection_item, thread_item, search_kongs, suggestion, s2_staff

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^kongtracker/', include('kongtracker.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    
    url(r'^$',          index,              name="kongtracker_index"), 
    url(r'^section/(?P<forum_section_id>\d+)/$',          section_item,              name="section_item"),
    url(r'^subsection/(?P<forum_subsection_id>\d+)/$',          subsection_item,              name="subsection_item"),
    url(r'^thread/(?P<thread_id>\d+)/$',          thread_item,              name="thread_item"),
    url(r'^search/$',          search_kongs,              name="search_kongs"), 
    url(r'^suggestion/$',          suggestion,              name="suggestion"),
    url(r'^s2staff/$',          s2_staff,              name="s2_staff"),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT})

    
)
