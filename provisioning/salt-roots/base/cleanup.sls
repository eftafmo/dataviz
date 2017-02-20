# various packages that might come pre-installed by the vagrant image
# or by a vanilla debian
cleanup-packages:
  pkg.purged:
    - pkgs:
        - dbus

        - debian-faq

        - exim4
        - exim4-base
        - exim4-daemon-light
        - exim4-config

        - laptop-detect
        - pciutils

        - mlocate
        - rename

        - tasksel
        - tasksel-data

        - telnet
