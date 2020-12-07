EEAG_REGION=westeurope
EEAG_RESOURCE_GROUP=we-p-fmo-docker-dataeeagrantsorg-rg
EEAG_VAULT=we-p-fmo-docker-dataeeagrantsorg-encryptionkey-vault
EEAG_STORAGE_ACCOUNT=wepfmodockerstorage

docker context list -q | grep -q $EEAG_RESOURCE_GROUP || docker context create aci $EEAG_RESOURCE_GROUP
export DOCKER_CONTEXT=$EEAG_RESOURCE_GROUP
PS1="[EEA Grants production]$PS1"
