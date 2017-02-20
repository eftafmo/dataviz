include:
  - base.apt

{%- from "application/map.jinja" import settings, IS_DEV with context %}
{%- from "application/uwsgi.sls" import socket_file %}
{%- set nginx_pkg = 'nginx-light' %}

nginx-installed:
  pkg.installed:
    - name: {{ nginx_pkg }}
    - fromrepo: stretch
    - require:
      - pkgrepo: apt-release-stretch
  # remove the default vhost conf
  file.absent:
    - name: /etc/nginx/sites-enabled/default
  service.running:
    - name: nginx
    - enable: True
    - require:
        - pkg: {{ nginx_pkg }}
        - sls: application.app

nginx-conf:
  file.managed:
    - name: /etc/nginx/sites-enabled/{{ settings.project_name }}
    - source: salt://application/files/nginx.vhost.conf
    - template: jinja
    - context:
        settings: {{ settings|json }}
        uwsgi_socket: {{ socket_file }}
        IS_DEV: {{ IS_DEV }}
    - watch_in:
        - service: nginx-installed
