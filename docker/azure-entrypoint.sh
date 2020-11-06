#!/bin/bash

set -e;

# copy nginx user config files
NGINX_USER_CONF=/etc/nginx/user.conf.d/
echo "Copying user config files to $NGINX_USER_CONF"
mkdir -p $NGINX_USER_CONF
(set -x; cp /nginxconfig/*.conf $NGINX_USER_CONF)

LETSENCRYPT_BACKUP=/nginxconfig/letsencrypt.tgz
if [ -f /nginxconfig/letsencrypt.tgz ]; then
  echo "Restoring letsencrypt data from $LETSENCRYPT_BACKUP"
  tar xz -C /etc < $LETSENCRYPT_BACKUP
fi

echo "Installing letsencrypt backup hook"
cat > /backup-letsencrypt.sh <<EOF
#!/bin/bash
set -x
tar cz -C /etc letsencrypt > $LETSENCRYPT_BACKUP
EOF

echo "Hacking /scripts/util.sh to call backup script when it's done"
cat >> /scripts/util.sh <<EOF
eval "\$(echo "orig_get_certificate()"; declare -f get_certificate | tail -n +2)"
get_certificate() {
  orig_get_certificate
  bash /backup-letsencrypt.sh
}
EOF


until grep -q web /etc/hosts; do
  echo "Waiting for 'web' in /etc/hosts ..."
  sleep 1
done
echo "Found 'web' in /etc/hosts, proceeding"

echo "Setting up environment variables"
export CERTBOT_EMAIL="eeagrants@edw.ro"
export ENVSUBST_VARS="FQDN"
export FQDN="eeagrants-azure.edw.ro"

echo "Running default entrypoint /scripts/entrypoint.sh ..."
exec /scripts/entrypoint.sh
