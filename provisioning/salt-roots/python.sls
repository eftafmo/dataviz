include:
  - base.apt

python-interpreter:
  pkg.installed:
    - name: python3
    - fromrepo: stretch
    - require:
      - pkgrepo: apt-release-stretch

python-pip-dependencies:
  pkg.installed:
    - pkgs:
        - python3-dev
        - build-essential
    - fromrepo: stretch
    - require:
      - pkg: python-interpreter

# we need this too because salt's pip_state fails otherwise
# when using pip3
python-pip2:
  pkg.installed:
    - name: python-pip

python-pip:
  pkg.installed:
    - name: python3-pip
    - fromrepo: stretch
    - require:
      - pkg: python-pip-dependencies
      - pkg: python-pip2

python-virtualenv:
  # we can install this from the repo instead
  #pip.installed:
  #  - name: virtualenv
  #  - bin_env: /usr/bin/pip3
  #  - require:
  #    - pkg: python-pip
  pkg.installed:
    - name: virtualenv
    - fromrepo: stretch
    - require:
      - pkg: python-interpreter

python-extras:
  pkg.installed:
    - pkgs:
        - ipython3
    - fromrepo: stretch
