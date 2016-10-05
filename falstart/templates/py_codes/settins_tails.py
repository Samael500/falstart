{# Append to settins.py file in init app provision #}


STATIC_URL = '/static/'
STATIC_ROOT = '{{ project_name }}/static'

TEST_RUNNER = 'rainbowtests.test.runner.RainbowDiscoverRunner'

{% if CELERY %}
# celery settings
broker_connection_link = {% if REDIS %}'redis://localhost:6379/0'{% else %}'amqp://guest:guest@localhost:5672//'{% endif %}

BROKER_URL = CELERY_RESULT_BACKEND = broker_connection_link
CELERY_ACCEPT_CONTENT = ['json', ]
{% endif %}

try:
    from settings_local import *  # noqa
except ImportError:
    pass
{# keep trailing newline #}