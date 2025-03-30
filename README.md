Webapp for Karma Tashi Ling buddhist centre, Norway
---------------------------------------------------

Built on `Django` and `Wagtail`.

## Requirements

### Software

- `git`
- `docker`
- `heroku`
- `bw` (DEV: fetching secrets in `./run` script)
- `psql` (DEV: dumping production db with `./import-heroku-db.sh`)

### Config

Environment variables:

- `STATIC_URL`: AWS S3 Bucket URL
- `MEDIA_URL`: AWS S3 Bucket URL
- `COMPRESS_STORAGE`: (PROD) `ktlweb.settings.s3storage.AWSStatic`
- `COMPRESS_URL`: (PROD) Same as `STATIC_URL`
- `ALLOWED_HOSTS`: (DEV) `localhost`

### Services

- Heroku app for the website.
- Google calendar for the website.
- AWS S3 for storing media and static files.

#### Google Calendar

Environment variables:

- `JWT_JSON_PATH` (DEV: Google oauth2 service account JSON JWT config)
- `GCAL_CLIENT_MAIL`: Service account credential
- `GCAL_PRIVATE_KEY`: Service account key

#### AWS S3

Environment variables:

- `AWS_MEDIA`: AWS S3 bucket name for Django media files
- `AWS_STATIC`: AWS S3 bucket name for Django static files
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

## Development

Ensure the following `.env` in project root directory,
but NOTE: **BE SURE TO INSERT VALID SECRETS FOR `<SECRET>`**

```
JWT_JSON_PATH=/data/gcal-jwt.json
AWS_MEDIA=ktlweb2-media-dev
AWS_STATIC=ktlweb2-static-dev
AWS_ACCESS_KEY_ID=<SECRET>
AWS_SECRET_ACCESS_KEY=<SECRET>
STATIC_URL=https://ktlweb2-static-dev.s3-eu-north-1.amazonaws.com/
MEDIA_URL=https://ktlweb-media-dev.s3-eu-west-1.amazonaws.com/
COMPRESS_STORAGE=ktlweb.settings.s3storage.AWSStatic
COMPRESS_URL=https://ktlweb2-static-dev.s3-eu-north-1.amazonaws.com/
ALLOWED_HOSTS=localhost
GCAL_CLIENT_MAIL=<SECRET>
GCAL_PRIVATE_KEY=<SECRET>
```

### Run

#### Docker

```sh
DOCKER_BUILDKIT=1 docker build -t ktlweb:dev .
./ensure-postgres.sh
./import-heroku-db.sh
./develop.sh
```

Page is served at http://localhost:8000

#### From scratch

1. ```sh
   python3 -m venv venv --prompt ktlweb
   venv/bin/pip install -U wheel
   venv/bin/pip install -U setuptools pip
   venv/bin/pip install -e .
   ```
2. Ensure environment variables are set according to shell script: `./run` 
   and [`dev.py`](ktlweb/settings/dev.py).
3. Import production DB: `./import-heroku-db.sh` or initialize new database:
    ```sh
    ./run makemigrations
    ./run migrate
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('d', '', 'd')" | ./run shell
    echo "from gcal.utils import db_init; db_init('d')" | ./run shell
    ```
4. Run server: `docker run -ti --env-file .env --rm -v $(pwd):/opt/ktlweb --entrypoint=bash ktlweb:dev`

### Technical debt

- [ ] Upgrade Wagtail
- [ ] Move Event streamfield objects to gcal app.
- [ ] UpcomingEventCentreChoiceField populates from Centre table.
- [ ] Centre has 1to1 key with calendar id.
