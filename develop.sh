#!/bin/bash

CONTAINER_STATUS=$(docker inspect ktlweb --format '{{ .State.Status }}' 2>/dev/null)

if [[ $? -eq 1 ]]; then
	CONTAINER_STATUS="null"
fi

set -eu -o pipefail

PY_VERSION=$(awk -F'[""]' '/requires-python/ {{ split($2, a, "="); print a[2]}}' pyproject.toml)

run_docker() {
	docker run \
		-ti \
		-d \
		--env-file .env \
		--name ktlweb \
		-e POSTGRES_DB="$POSTGRES_DB" \
		-e SECRET_KEY="$SECRET_KEY" \
		-e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
		-e DATABASE_URL="$DATABASE_URL" \
		-e DJANGO_SETTINGS_MODULE=ktlweb.settings.dev \
		-e WAGTAIL_DEBUG=True \
		-p 8000:8000 \
		-v "$(pwd)/src:/opt/ktlweb/src" \
		-v "$(pwd)/jwt/gcal-jwt.json:/opt/ktlweb/jwt/gcal-jwt.json:ro" \
		--network ktlweb \
		"ktlweb:$PY_VERSION" \
		runserver 0.0.0.0:8000
}

dev_docker() {
	docker run \
		-ti \
		--env-file .env \
		--name ktlweb \
		-e POSTGRES_DB="$POSTGRES_DB" \
		-e SECRET_KEY="$SECRET_KEY" \
		-e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
		-e DATABASE_URL="$DATABASE_URL" \
		-e DJANGO_SETTINGS_MODULE=ktlweb.settings.dev \
		-e WAGTAIL_DEBUG=True \
		-p 8000:8000 \
		-v "$(pwd)/pyproject.toml:/opt/ktlweb/pyproject.toml" \
		-v "$(pwd)/src:/opt/ktlweb/src" \
		-v "$(pwd)/jwt/gcal-jwt.json:/opt/ktlweb/jwt/gcal-jwt.json:ro" \
		--network ktlweb \
		--entrypoint bash \
		"ktlweb:$PY_VERSION"
}

case $CONTAINER_STATUS in
"null")
	POSTGRES_DB=ktlweb_db
	SECRET_KEY="$(bw get password ktlweb_secret_key)"
	POSTGRES_PASSWORD=$(bw get password ktlweb_db)
	DATABASE_URL="postgres://postgres:$POSTGRES_PASSWORD@ktlweb_db/$POSTGRES_DB"

	set +e
	mkdir jwt 2>/dev/null
	set -e

	bw get notes ktlweb-dev-gcal-jwt-json > jwt/gcal-jwt.json

	run_docker
	;;
"running")
	echo ktlweb container running
	;;
"exited")
	docker start ktlweb
	;;
esac
