#!/bin/bash

set -eu -o pipefail

PY_VERSION=$(awk -F'[""]' '/requires-python/ {{ split($2, a, "="); print a[2]}}' pyproject.toml)

docker run \
	-ti \
	--rm \
	--env-file .env \
	--name ktlweb-update-deps \
	-e DJANGO_SETTINGS_MODULE=ktlweb.settings.dev \
	-p 8000:8000 \
	-v "$(pwd)/pyproject.toml:/opt/ktlweb/pyproject.toml" \
	-v "$(pwd)/uv.lock:/opt/ktlweb/uv.lock" \
	-v "$(pwd)/src:/opt/ktlweb/src" \
	-v "$(pwd)/jwt/gcal-jwt.json:/opt/ktlweb/jwt/gcal-jwt.json:ro" \
	--network ktlweb \
	--entrypoint bash \
	"ktlweb:$PY_VERSION"
