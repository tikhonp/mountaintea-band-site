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

docker run -d --name temp_restore_container -v mountaintea-media-data:/backup_restore alpine
docker cp backup-data-cache/backup/media-backup temp_restore_container:/backup_restore
docker stop temp_restore_container
docker rm temp_restore_container

docker run -d --env-file .env --name postgres-backup-restore -v mountaintea-db-data:/var/lib/postgresql/data postgres:17
set -o allexport && source .env && set +o allexport
until docker exec -i postgres-backup-restore pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
    sleep 0.1;
done;
sleep 3; # fuck it sleep while waiting for db creation
docker exec -i postgres-backup-restore psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < backup-data-cache/backup/db-backup/mountaintea-db.dump
docker stop postgres-backup-restore
docker rm postgres-backup-restore

rm -rf backup-data-cache
