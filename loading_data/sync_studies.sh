#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

. "$DIR""/../.envs/.production/.django_prod"
. "$DIR""/../.envs/.production/.postgres_prod"
. "$DIR""/../.env"

export COMPOSE_PROJECT_NAME

CELERY_BROKER_URL="${REDIS_URL}"
DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
STUDIES_FOLDER="/app/loading_data/rgv_data/studies"
SYNC_FILE="/groups/irset/archives/web/RGV2/auto_sync_studies/metadata.csv"

if [ -f "$SYNC_FILE" ]; then
   echo "Metadata file found. Adding studies..."
   /usr/local/bin/docker-compose -f "$DIR""/../production.yml" exec -T -e DATABASE_URL=$DATABASE_URL -e CELERY_BROKER_URL=$CELERY_BROKER_URL django python manage.py sync_studies \
        "/rgv_data/auto_sync_studies/metadata.csv" \
        "/rgv_data/"
   rm "$SYNC_FILE"
fi
