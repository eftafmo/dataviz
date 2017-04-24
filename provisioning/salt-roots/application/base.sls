{%- from "application/map.jinja" import settings, IS_DEV with context -%}

# basic prerequisites
application-user:
  group.present:
    - name: {{ settings.group }}
  user.present:
    - name: {{ settings.user }}
    - gid: {{ settings.group }}
{#
{%- if not IS_DEV %}
    # set the project root as user's home on production
    - home: {{ settings.root_dir }}
{%- endif %}
#}
    - empty_password: True
    - require:
        - group: {{ settings.group }}

application-root-dir:
  # creating this first because the order below is unpredictable
  file.directory:
    - name: {{ settings.root_dir }}
    - user: {{ settings.user }}
    - group: {{ settings.group }}
    - require:
        - user: application-user

application-dirs:
  file.directory:
    - names:
        - {{ settings.webroot_dir }}
        - {{ settings.etc_dir }}
        - {{ settings.run_dir }}
        - {{ settings.log_dir }}
    - user: {{ settings.user }}
    - group: {{ settings.group }}
    - require:
        - file: application-root-dir

application-webserver-user:
  # add httpd user to app's user group
  user.present:
    - name: {{ settings.www_user }}
    - groups:
      - {{ settings.group }}
    - remove_groups: False
    - require:
      - user: application-user
