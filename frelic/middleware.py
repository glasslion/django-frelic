"""
django-frelic middleware
"""
import time
import re


from django.conf import settings
from django.utils.encoding import smart_str, force_text
from django.template import Template
from django.test.signals import template_rendered
from django.test.utils import instrumented_test_render

from .core import Frelic


_HTML_TYPES = ('text/html', 'application/xhtml+xml')


# Monkey-patch to enable the template_rendered signal. The receiver returns
# immediately when the panel is disabled to keep the overhead small.

# Code taken and adapted from Simon Willison and Django Snippets:
# http://www.djangosnippets.org/snippets/766/

if Template._render != instrumented_test_render:
    Template.original_render = Template._render
    Template._render = instrumented_test_render


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

        content = force_text(response.content, encoding=settings.DEFAULT_CHARSET)

        response.content = content.replace(u"<!-- /* FRELIC DATA */ -->", ga_code)
        
        if response.get('Content-Length', None):
            response['Content-Length'] = len(response.content)

        return response
