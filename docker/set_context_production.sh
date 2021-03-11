EEAG_REGION=westeurope
EEAG_RESOURCE_GROUP=we-p-fmo-docker-dataeeagrantsorg-rg
EEAG_VAULT=we-p-fmo-dataeeag-vault
EEAG_STORAGE_ACCOUNT=wepfmodockerstorage
export COMPOSE_PROJECT_NAME=we-p-fmo-docker-dataeeagrantsorg-cg

docker context list -q | grep -q $EEAG_RESOURCE_GROUP || docker context create aci $EEAG_RESOURCE_GROUP
export DOCKER_CONTEXT=$EEAG_RESOURCE_GROUP
PS1="[EEA Grants production]$PS1"
