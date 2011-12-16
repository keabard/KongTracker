# -*- encoding: utf-8 -*-

#-- Django imports
from django.views.generic.simple import direct_to_template
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.db.models import Max

def get_decoded_text(text):
    if text :
        try:
            return unicode(text)
        except UnicodeDecodeError:
            try:
                decoded_chunk = text.decode('utf-8')
                return decoded_chunk
            except UnicodeDecodeError:
                try:
                    decoded_chunk = text.decode('iso-8859-1')
                    return decoded_chunk
                except UnicodeDecodeError:
		    try:
                        decoded_chunk = text.decode('latin1')
                        return decoded_chunk
                    except UnicodeDecodeError:
                        error_msg = _("File encoding unknown")
                        raise RollbackRequiredException(error_msg)
    return text

def get_encoded_text(text, encoding='utf-8'):
    if not text:
        return ''
    if type(text)==StringType:
        return text
    elif type(text)==UnicodeType:
        return text.encode(encoding, 'ignore')
    else:
        try:
            text=repr(text)
            return text
        except:
            raise BaseException('Cannot encode a non text argument that cannot repr : %s'%text)
