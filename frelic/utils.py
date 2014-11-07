
DEPLOYED_VERSION_SLOT = 5 


def generate_ga_code(data):
    

    timing = [
        ('Django Freelic Views', 'Response time (Total)', data['resp_time'], data['view_name']),
        ('Django Freelic Views', 'Response time (SQL Queries)', data['resp_time'], data['view_name']),
        ('Django Freelic Views', 'Response time (Templates)', data['sqltime'], data['view_name']),
    ]

    context['timing'] = timing
    

    # {
    #     'google_analytics_id': settings.GOOGLE_ANALYTICS_ID,
    #     'report_deployed_version': "11",
    # }