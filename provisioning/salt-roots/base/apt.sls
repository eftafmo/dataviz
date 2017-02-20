apt-release-stretch:
  pkgrepo.managed:
    - name: deb http://deb.debian.org/debian stretch main

apt-configuration:
  file.recurse:
    - name: /etc/apt
    - source: salt://base/files/apt
    - required_in:
        - pkgrepo: apt-release-stretch
