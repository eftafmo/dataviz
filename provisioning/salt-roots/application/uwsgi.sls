include:
  - base.apt
  - .base
  - .app

{%- from "application/map.jinja" import settings, IS_DEV with context -%}

{%- set service = "uwsgi-%s.service" % settings['project_name'] %}
{%- set service_file = salt['file.join']('/etc/systemd/system/', service) %}
{%- set conf_file = salt['file.join'](settings['etc_dir'], 'uwsgi.ini') %}
{%- set socket_file = salt['file.join'](settings['run_dir'], 'uwsgi.socket') %}
# TODO: move away local knowledge of project structure
{%- set wsgi_file = 'dv/wsgi.py' %}

uwsgi-installed:
  pkg.installed:
    - pkgs:
        - uwsgi
        - uwsgi-plugin-python3
    - fromrepo: stretch
    - require:
      - pkgrepo: apt-release-stretch
  # we don't need to run the default uwsgi service
  service.disabled:
    - name: uwsgi

uwsgi-conf:
  file.managed:
    - name: {{ conf_file }}
    - makedirs: True
    - source: salt://application/files/uwsgi.ini
    - template: jinja
    - context:
        settings: {{ settings|json }}
        socket: {{ socket_file }}
        wsgi_file: {{ wsgi_file }}
        IS_DEV: IS_DEV
    - require:
        - user: application-user

uwsgi-service:
  file.managed:
    - name: {{ service_file }}
    - source: salt://application/files/uwsgi.service
    - template: jinja
    - context:
        settings: {{ settings|json }}
        conf_file: {{ conf_file }}
        IS_DEV: IS_DEV
    - require:
        - uwsgi-installed
  # reload systemd config
  module.wait:
    - name: service.systemctl_reload
    - watch:
        - file: {{ service_file }}
  service.running:
    - name: {{ service }}
    - enable: True
    - require:
        - file: {{ service_file }}
        - file: uwsgi-conf
        - virtualenv: app-virtualenv
        - file: app-setup
    - watch:
        - file: {{ service_file }}
        - file: uwsgi-conf
