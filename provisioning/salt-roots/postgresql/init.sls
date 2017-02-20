include:
  - base.apt

{% set settings = {
  'db': pillar['project_name'],
  'user': pillar['user'],
} %}

{% do settings.update(salt['pillar.get']('postgresql', {})) %}

postgresql-installed:
  pkg.installed:
    - name: postgresql-9.6
    - fromrepo: stretch
    - require:
        - pkgrepo: apt-release-stretch

postgresql-user:
  postgres_user.present:
    - name: {{ settings.user }}
    - require:
        - pkg: postgresql-installed

postgresql-database:
  postgres_database.present:
    - name: {{ settings.db }}
    - owner: {{ settings.user }}
    - require:
        - postgres_user: postgresql-user
