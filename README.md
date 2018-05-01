Webapp for Karma Tashi Ling buddhist centre, Norway
---------------------------------------------------

Built on `Django` and `Wagtail`.

### Requirements

* `PostgreSQL` > 9.4 (or Docker)
* [pipenv](https://docs.pipenv.org/)

### Install

* `pipenv install`.
* Install `PostgreSQL` and configure a DB, or with Docker:

```bash
docker run \
    --name ktlweb_db \
    -d \
    -P \
    -e POSTGRES_PASSWORD=<some password> \
    -e POSTGRES_DB=ktlweb_db \
    postgres:9.6.1
```

### Config

- `JWT_JSON_PATH`: Google oauth2 service account JSON JWT config.
- `AWS_MEDIA`: AWS S3 bucket name for Django media files
- `AWS_STATIC`: AWS S3 bucket name for Django static files
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `STATIC_URL`: Bucket URL
- `MEDIA_URL`: Bucket URL
- `COMPRESS_STORAGE`: `ktlweb.settings.s3storage.AWSStatic` (Production only)
- `COMPRESS_URL`: Same as `STATIC_URL` (Production only)
- `ALLOWED_HOSTS`: `localhost` for development
- `GCAL_CLIENT_MAIL`: Service account credential
- `GCAL_PRIVATE_KEY`: Service account key

### Run

1. `pipenv shell`
2. Ensure environment variables are set according to shell script: `run` and `dev.py`. (Shell script uses `gpass.sh` to fetch secrets, replace with personal preference.)
3. Build database:
    - `./run makemigrations`
    - `./run migrate`
4. Create super user (name & password: `d`): `echo "from django.contrib.auth.models import User; User.objects.create_superuser('d', '', 'd')" | ./run shell`
5. Initialize calendar entries from Google Calendar (optional): `echo "from gcal.utils import db_init; db_init('d')" | ./run shell`
5. Run server: `./run runserver`
