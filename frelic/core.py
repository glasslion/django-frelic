import time

from django.conf import settings
from django.db import connection
from django.template.loader import render_to_string

class Frelic(object):
    """docstring for Frelic"""

    def __init__(self):
        self.start_time = time.time()
        self.template_num = 0 

    def set_view_name(self, view_func):
        self.view_name = ".".join((view_func.__module__, view_func.__name__))

    def count_templates(self, sender, **kwargs):
        self.template_num += 1

    def load_metrics(self):
        self.timings = []
        self.counts = []

        total_time = (time.time() - self.start_time) * 1000
        self.add_timing("Total time", total_time)

        self.sql_query_num = len(connection.queries)

        self.add_count('Rendered Templates', self.template_num)
        self.add_count('SQL Queries', self.sql_query_num)

        sql_time = 0.0
        for query in connection.queries:
            query_time = float(query.get('time', 0)) * 1000
            if query_time == 0:
                # django-debug-toolbar monkeypatches the connection
                # cursor wrapper and adds extra information in each
                # item in connection.queries. The query time is stored
                # under the key "duration" rather than "time" and is
                # in milliseconds, not seconds.
                query_time = query.get('duration', 0) 
            sql_time += query_time
        self.add_timing("SQL Query Time", sql_time)

    def add_timing(self, name, millisec):
        self.timings.append(('Frelic', name, millisec, self.view_name))

    def add_count(self, name, count):
        self.counts.append(('Frelic', name, count, self.view_name))

    def ga_code(self):
        context = {}
        context['google_analytics_id'] = settings.GOOGLE_ANALYTICS_ID
        context['timings'] = self.timings
        context['counts'] = self.counts
        return render_to_string('frelic/ga_code.html', context)




