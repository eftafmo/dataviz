```
cd dataviz/provisioning

cp salt-config/minion.example salt-config/minion
cp salt-pillar/settings.sls.example salt-pillar/settings.sls
# edit them if necessary ^^

salt-call state.apply

# you may want to edit dv/localsettings.py
# and `systemctl restart uwsgi-dataviz.service`

```
