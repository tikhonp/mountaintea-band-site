#!/bin/bash

if [ -z "$1" ]
  then
    echo "No backup archive URL provided"
    exit
fi

mkdir -p backup-data-cache
curl -sL "$1" | tar xvzf - -C backup-data-cache/

docker volume rm mountaintea-db-data -f || exit
docker volume rm mountaintea-media-data -f || exit

docker run --rm --name temp_restore_container \
    --mount type=volume,src=mountaintea-media-data,dst=/backup_restore \
    -v ./backup-data-cache/backup/media-backup/:/backup_source:ro \
    alpine \
        cp -r /backup_source /backup_restore

docker run --rm \
  --env-file .env \
  --name postgres-backup-restore \
  -v ./backup-data-cache/backup/:/backup_restore \
  --mount type=volume,src=mountaintea-db-data,dst=/var/lib/postgresql/data \
  postgres:17-alpine \
  sh -c '
    docker-entrypoint.sh postgres &
    until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do sleep 0.5; done;
    sleep 2;
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < /backup_restore/db-backup/mountaintea-db.dump
  '
rm -rf backup-data-cache
