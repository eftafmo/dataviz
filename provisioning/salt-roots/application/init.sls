{%- from "application/map.jinja" import settings, IS_DEV with context -%}

# basic prerequisites
application-user:
  user.present:
    - name: {{ settings.user }}
{#
{%- if not IS_DEV %}
    # set the project root as user's home on production
    - home: {{ settings.root_dir }}
{%- endif %}
#}
    - empty_password: True

application-dirs:
  file.directory:
    - names:
        - {{ settings.root_dir }}
        - {{ settings.webroot_dir }}
        - {{ settings.etc_dir }}
        - {{ settings.run_dir }}
        - {{ settings.log_dir }}
    - user: {{ settings.user }}
    - require:
        - user: application-user

include:
  - .app
  - .uwsgi
  - .nginx
