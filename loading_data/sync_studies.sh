#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

. "$DIR""/../.envs/.production/.django"
. "$DIR""/../.envs/.production/.postgres"

CELERY_BROKER_URL="${REDIS_URL}"
DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
STUDIES_FOLDER="/app/loading_data/rgv_data/studies"


if [ -f "$ADD_FILE" ]; then
   echo "Metadata file found. Adding studies..."
   docker-compose -f "$DIR""/../production.yml" exec -e DATABASE_URL=$DATABASE_URL -e CELERY_BROKER_URL=$CELERY_BROKER_URL django python manage.py sync_studies "/app/loading_data/sync/metadata.csv" "/mnt/"
   rm "$ADD_FILE"
fi
