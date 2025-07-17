SOURCE_COMMIT_SHA := $(shell git rev-parse HEAD)

ENVS := SOURCE_COMMIT=${SOURCE_COMMIT_SHA} COMPOSE_BAKE=true


.PHONY: run dev fdev build-dev prod fprod logs-prod go-to-server-container migrations backup

run: dev

dev:
	${ENVS} docker compose -f compose.yaml up

build-dev:
	${ENVS} docker compose -f compose.yaml up --build

fdev:
	${ENVS} docker compose -f compose.yaml down

prod:
	${ENVS} docker compose -f compose.prod.yaml up --build -d

fprod:
	${ENVS} docker compose -f compose.prod.yaml down

logs-prod:
	${ENVS} docker compose -f compose.prod.yaml logs -f -n 100

go-to-server-container:
	docker exec -it --tty mountaintea-server /bin/bash

migrations:
	docker compose -f compose.makemigrations.yaml up --build --abort-on-container-exit

backup:
	 docker exec mountaintea-backup backup
