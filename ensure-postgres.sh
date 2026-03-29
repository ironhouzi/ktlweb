#!/bin/bash

POSTGRES_DB=ktlweb_db
DB_CONTAINER_STATUS=$(docker inspect "$POSTGRES_DB" --format '{{ .State.Status }}' 2>/dev/null)

if [[ $? -eq 1 ]]; then
	DB_CONTAINER_STATUS="null"
fi

# Error if exists. Hence, idempotent.
docker network create ktlweb 2>/dev/null

set -eu -o pipefail

docker_run() {
	echo -n 'Fetching Heroku Postgres version ..'
	PG_VERSION=$(heroku pg:info --app ktlweb-prod2 \
		| grep 'PG Version:' \
		| awk '{ split($0, a, ":"); print a[2] }' \
		| tr -d '[:space:]')

	echo ": $PG_VERSION"

	docker run \
	    --name "$POSTGRES_DB" \
	    -P \
	    -e POSTGRES_PASSWORD="$(bw get password ktlweb_db)" \
	    -d \
	    --network ktlweb \
	    "postgres:$PG_VERSION"
}

case $DB_CONTAINER_STATUS in
"null")
	docker_run
	;;
"created")
	docker rm -f -v "$POSTGRES_DB"
	docker_run
	;;
"running")
	echo postgres container running
	;;
"exited")
	docker start "$POSTGRES_DB"
	;;
esac
