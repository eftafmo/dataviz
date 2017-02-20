include:
  - .apt
  - .cleanup

# packages that we definitely need to have installed, always
base-packages:
  pkg.installed:
    - pkgs:
        - sudo
