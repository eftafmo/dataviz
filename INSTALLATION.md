```
cd dataviz/provisioning

cp salt-config/minion.example salt-config/minion
cp salt-pillar/settings.sls.example salt-pillar/settings.sls
# edit them if necessary ^^

salt-call state.apply

# if you edit dv/localsettings.py don't forget to 
systemctl restart uwsgi-dataviz.service

```
