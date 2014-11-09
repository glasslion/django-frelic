"""
django-frelic middleware
"""
from pprint import pprint
import time
import re


from django.conf import settings
from django.utils.encoding import smart_str
from django.test.signals import template_rendered

from .core import Frelic


_HTML_TYPES = ('text/html', 'application/xhtml+xml')


class FrelicMiddleware(object):
    def process_request(self, request):
        request._frelic = Frelic()
        template_rendered.connect(request._frelic.count_templates)


    def process_view(self, request, view_func, view_args, view_kwargs):
        if not hasattr(request, '_frelic'):
            return
        request._frelic.set_view_name(view_func)


    def process_response(self, request, response):

        if not hasattr(request, '_frelic'):
            return response

        template_rendered.disconnect(request._frelic.count_templates)

        if response.status_code != 200:
            return response

        # Check for responses where the toolbar can't be inserted.
        content_encoding = response.get('Content-Encoding', '')
        content_type = response.get('Content-Type', '').split(';')[0]
        if any((getattr(response, 'streaming', False),
                'gzip' in content_encoding,
                content_type not in _HTML_TYPES)):
            return response

        request._frelic.load_metrics()

        ga_code = request._frelic.ga_code()

        response.content = response.content.replace("<!-- /* FRELIC DATA */ -->", ga_code)
        
        if response.get('Content-Length', None):
            response['Content-Length'] = len(response.content)

        return response
