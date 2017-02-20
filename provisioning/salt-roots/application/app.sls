include:
  - base.apt
  - python

{%- from "application/map.jinja" import settings, IS_DEV with context -%}

{%- set _reqs = 'requirements%s.txt' % ('.dev' if IS_DEV else '') %}
{%- set reqs_file = salt['file.join'](settings.repo_dir, _reqs) %}
{%- set sys_reqs_file = salt['file.join'](settings.repo_dir, 'sysrequirements.txt') %}

# install some requirements system-wide
{% set sys_reqs = salt['cmd.shell'](
    """grep -o '^[a-zA-Z0-9_-]\+' """ + sys_reqs_file
).splitlines() %}

{% if sys_reqs %}
app-system-requirements:
  pkg.installed:
    - pkgs:
{%- for req in sys_reqs %}
        - python3-{{ req }}
{% endfor %}
    - fromrepo: stretch
    - require:
      - pkgrepo: apt-release-stretch
{% endif %}

app-virtualenv:
  virtualenv.managed:
    - name: {{ settings.venv_dir }}
    - python: python3.5
    - system_site_packages: True
    - user: {{ settings.user }}
    - requirements: {{ reqs_file }}
    - require:
      - pkg: python-virtualenv
      - user: application-user
      - file: application-dirs

# TODO: checkout from git on production / staging,
# but use the already-mounted directory on dev

# app-deployment-deps:
#   pkg.installed:
#     - name: git
