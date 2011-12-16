# -*- encoding: utf-8 -*-

#-- Django imports
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

#-- Models
    
class KongThread(models.Model):
    """
        A Kong Thread can point to a ForumSubSection or a ForumSection
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object =  generic.GenericForeignKey()
    
    thread_id = models.IntegerField('HoN Forum Thread ID')
    link = models.CharField('Link', max_length = 250)
    title = models.CharField('Title', max_length = 250)
    last_modified = models.DateTimeField('Last kong post', blank = True,  null = True)

class KongPost(models.Model):
    
    kong_thread = models.ForeignKey(KongThread)
    forum_id = models.IntegerField('HoN Forum Post ID')
    author = models.CharField('Author',  max_length = 250)
    date = models.DateTimeField('Post date')
    link = models.CharField('Link', max_length = 250)
    message = models.TextField('Message')

class ForumSection(models.Model):
    link = models.CharField('Link', max_length = 250)
    title = models.CharField('Title', max_length = 250)
    threads = generic.GenericRelation(KongThread)
    
class ForumSubSection(models.Model):
    forum_section = models.ForeignKey(ForumSection)
    link = models.CharField('Link', max_length = 250)
    title = models.CharField('Title', max_length = 250)
    threads = generic.GenericRelation(KongThread)
