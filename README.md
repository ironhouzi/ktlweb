Webapp for Karma Tashi Ling buddhist center, Norway
---------------------------------------------------

Built on `Django` and `Wagtail`.

###Requirements

* Python 3 compiled with `pip` and `virtualenv` support.
* `PostgreSQL` > 9.4 (or Docker)
* `ElasticSearch v.1`

###Install

1. `pyvenv venv`.
2. `source venv/bin/activate`.
3. `pip install requirements.txt`.
4. Install `PostgreSQL` and configure a DB, or with Docker:
```bash
docker run \
    --name ktlweb_db \
    -d \
    -P \
    -e POSTGRES_PASSWORD=<some password> \
    -e POSTGRES_DB=ktlweb_db \
    postgres:9.4
```
5. Install `ElasticSearch v.1`, or with Docker:
```bash
docker run --name ktlweb_es -d -P elasticsearch:1
```
6. Ensure environment variables are set according to shell script: `run` and `dev.py`. (Shell script uses `gpass.sh` to fetch secrets, replace with personal preference.)
7. Build database:
* `./run makemigrations`
* `./run migrate`
8. Create super user: `./run createsuperuser`
9. Run server: `./run runserver`
