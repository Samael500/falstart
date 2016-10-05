

"""
Since this line until the end of file is helpfull code which should be
automatically removed at the end of deployment box. If occurred errors
and boxing has not made a complete build. It is necessary to correct
the errors and manually delete the code.
"""

from jinja2 import Environment, FileSystemLoader

def render_to_string(template_name):
    """ Render template to string """
    # load jinja template
    jinja_env = Environment(loader=FileSystemLoader(VARS['templates_dir']))
    template = jinja_env.get_template(template_name)
    # write to remote file
    return target_file.write(template.render(**VARS))


def app():
    """ Run application tasks """
    with cd(VARS['root_dir']):
        # Create venv and install requirements
        run('pyvenv-{{ pyenv_version }} {venv_path}'.format(**VARS))
        # make wheels for python packages
        run('{venv_path}/bin/pip install -U pip wheel'.format(**VARS))
        run('mkdir -p wheels')
        run('{venv_path}/bin/pip wheel -w wheels/ -r requirements-remote.txt --pre'.format(**VARS))
        # Install required python packages with pip from wheels archive
        run('make wheel_install')
        # run app tasks for devserver start
        start_app()
        # Copy settings local
        run('cd {project_name} && cp settings_local.py.example settings_local.py'.format(**VARS))


def start_app():
    """ start dj app """
    with fabric.context_managers.settings(warn_only=True):
        run('{venv_path}/bin/django-admin startproject {project_name} .'.format(**VARS))

    with open('{project_name}/settings.py'.format(**VARS), 'r') as settings_file:
        settings = settings_file.read()

    # make replacements
    settings = settings.replace(
        dedent(
        '''\
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        '''),
        dedent(
        '''\
            import sys

            BASE_DIR = os.path.dirname(os.path.dirname(__file__))

            if __name__ in ['settings', '{project_name}.settings']:
                sys.path.insert(0, os.path.join(BASE_DIR, '{project_name}'))
        '''.format(**VARS)
        )
    )

    {% if POSTGRES %}
    settings = settings.replace(
        dedent('''\
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
                }
            }
        '''),
        dedent('''\
            DATABASES = {{
                'default': {{
                    'ENGINE': 'django.db.backends.postgresql_psycopg2',
                    'NAME': '{db_name}',
                    'USER': '{db_user}',
                    'PASSWORD': '{db_password}',
                    'HOST': '127.0.0.1',
                }}
            }}'''.format(**VARS)
        )
    {% endif %}

    settings += render_to_string('includes/settings_tail.py')
    with open('{project_name}/settings.py'.format(**VARS), 'w') as settings_file:
        settings_file.write(settings)

    {% if CELERY %}
        with open('{project_name}/__init__.py'.format(**VARS), 'w') as init_file:
            init_file.write(render_to_string('includes/celery_init.py'))
    {% endif %}