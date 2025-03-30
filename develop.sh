#!/bin/bash

CONTAINER_STATUS=$(docker inspect ktlweb --format '{{ .State.Status }}' 2>/dev/null)

if [[ $? -eq 1 ]]; then
	CONTAINER_STATUS="null"
fi

set -eu -o pipefail

case $CONTAINER_STATUS in 
"null")
	export POSTGRES_DB=ktlweb_db
	export SECRET_KEY="$(bw get password ktlweb_secret_key)"
	export POSTGRES_PASSWORD=$(bw get password ktlweb_db)
	export DATABASE_URL="postgres://postgres:$POSTGRES_PASSWORD@ktlweb_db/$POSTGRES_DB"

	set +e
	mkdir jwt 2>/dev/null
	set -e

	bw get notes ktlweb-dev-gcal-jwt-json > jwt/gcal-jwt.json

	docker run \
		-ti \
		-d \
		--env-file .env \
		--name ktlweb \
		-e POSTGRES_DB=$POSTGRES_DB \
		-e SECRET_KEY=$SECRET_KEY \
		-e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
		-e DATABASE_URL=$DATABASE_URL \
		-e DJANGO_SETTINGS_MODULE=ktlweb.settings.dev \
		-e WAGTAIL_DEBUG=True \
		-p 8000:8000 \
		-v $(pwd):/opt/ktlweb \
		-v $(pwd)/jwt/gcal-jwt.json:/data/gcal-jwt.json:ro \
		--network ktlweb \
		ktlweb:dev \
		runserver 0.0.0.0:8000
	;;
"running")
	echo ktlweb container running
	;;
"exited")
	docker start ktlweb
	;;
esac
