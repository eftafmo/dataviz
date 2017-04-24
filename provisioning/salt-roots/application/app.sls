include:
  - base.apt
  - python
  - .base

{%- from "application/map.jinja" import settings, IS_DEV with context %}

# TODO: checkout from git on production / staging,
# but use the already-mounted directory on dev
app-repo:
  pkg.installed:
    - name: git
  git.latest:
    - name: {{ settings.repo }}
    - target: {{ settings.repo_dir }}
    - user: {{ settings.user }}
    # make sure this works even when upstream history was rewritten
    - force_reset: True
    - force_fetch: True
    - require:
      - pkg: git
      - file: application-dirs


{%- set _reqs = 'requirements%s.txt' % ('.dev' if IS_DEV else '') %}
{%- set reqs_file = salt['file.join'](settings.repo_dir, _reqs) %}

{#
## NOTE: this was a good idea but is too frail:
##       1) the repo needs to exist prior to `sys_reqs` being evaluated
##       2) the relationship between repo names and pypi names is unpredictable
## TODO: improve it.
##
# {%- set sys_reqs_file = salt['file.join'](settings.repo_dir, 'sysrequirements.txt') %}
# # install some requirements system-wide
# {% set sys_reqs = salt['cmd.shell'](
#     """grep -o '^[a-zA-Z0-9_-]\+' """ + sys_reqs_file
# ).splitlines() %}
#
# {% if sys_reqs %}
# app-system-requirements:
#   pkg.installed:
#     - pkgs:
# {%- for req in sys_reqs %}
#         - python3-{{ req }}
# {% endfor %}
#     - fromrepo: stretch
#     - require:
#       - pkgrepo: apt-release-stretch
# {% endif %}
#}

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
      - git: app-repo

# TODO: move away local knowledge of project structure
{%- set lsettings_file = salt['file.join'](settings.repo_dir, "dv/localsettings.py") %}

# also TODO: this should be set up from pillar variables and local templates
app-pre-setup:
  file.copy:
    - name: {{ lsettings_file }}
    - source: {{ lsettings_file }}.example
    - require:
        - git: app-repo

app-setup:
  file.replace:
    - name: {{ lsettings_file }}
    - pattern: |-
        ^ALLOWED_HOSTS *= *\[\]$
    - repl: |-
        ALLOWED_HOSTS = ["{{ settings.hostname }}"]
    - require:
        - file: app-pre-setup
