#!/bin/bash

POSTGRES_DB=ktlweb_db
DB_CONTAINER_STATUS=$(docker inspect $POSTGRES_DB --format '{{ .State.Status }}' 2>/dev/null)

if [[ $? -eq 1 ]]; then
	echo 'No postgres container running! Execute `./run` first!'
fi

set -eu -o pipefail

case $DB_CONTAINER_STATUS in 
"running")
	echo postgres container running
	;;
"exited")
	docker start $POSTGRES_DB
	;;
esac

echo -n 'Fetching Heroku Postgres instance ..'
export HEROKU_DB=$(heroku pg:info \
	| grep 'Add-on' \
	| awk '{ split($0, a, ":"); print a[2] }' \
	| tr -d '[:space:]')
echo ": $HEROKU_DB"

PG_PORT=$(docker port $POSTGRES_DB | grep '0.0.0.0' | cut -d : -f2)
PGUSER=postgres \
PGPASSWORD=$(bw get password $POSTGRES_DB) \
PGHOST=127.0.0.1 \
PGPORT=$PG_PORT \
	heroku pg:pull $HEROKU_DB $POSTGRES_DB
