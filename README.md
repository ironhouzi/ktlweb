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

### Run

1. `pipenv shell`
2. Ensure environment variables are set according to shell script: `run` and `dev.py`. (Shell script uses `gpass.sh` to fetch secrets, replace with personal preference.)
3. Build database:
    - `./run makemigrations`
    - `./run migrate`
4. Create super user: `./run createsuperuser`
5. Run server: `./run runserver`
