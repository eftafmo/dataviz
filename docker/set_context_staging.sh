EEAG_REGION=northeurope
EEAG_RESOURCE_GROUP=eeagstaging
EEAG_VAULT=eeagsecrets
EEAG_STORAGE_ACCOUNT=eeagstorage

docker context list -q | grep -q $EEAG_RESOURCE_GROUP || docker context create aci $EEAG_RESOURCE_GROUP
export DOCKER_CONTEXT=$EEAG_RESOURCE_GROUP
PS1="[EEA Grants staging]$PS1"
