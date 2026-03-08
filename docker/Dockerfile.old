FROM python:3.9.17

ENV CONTAINER_APP_DEST /opt/ktlweb
ENV APP_USER ktlweb
ENV APP_PORT 8000
ENV DJANGO_SETTINGS_MODULE ktlweb.settings.dev
ENV WAGTAIL_DEBUG True
ENV DATABASE_URL postgres://postgres:ktl@db/ktlweb_db

RUN apt-get update && apt-get install -y locales && locale-gen nb_NO.UTF-8 && \
    echo "Europe/Oslo" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# nb_NO.UTF-8 UTF-8/nb_NO.UTF-8 UTF-8/' /etc/locale.gen && \
    echo 'LANG="nb_NO.UTF-8"'>/etc/default/locale && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=nb_NO.UTF-8

RUN groupadd -r $APP_USER && useradd -r -g $APP_USER $APP_USER -d $CONTAINER_APP_DEST
ADD requirements.txt $CONTAINER_APP_DEST/

RUN python3 -m venv /venv --prompt ktlweb
RUN /venv/bin/pip install -U wheel
RUN /venv/bin/pip install -U pip setuptools
RUN /venv/bin/pip install -r $CONTAINER_APP_DEST/requirements.txt

RUN mkdir -p /opt/static
RUN mkdir -p /opt/media
RUN chown -R $APP_USER:$APP_USER /opt

USER $APP_USER
WORKDIR $CONTAINER_APP_DEST
EXPOSE $APP_PORT

ENTRYPOINT ["/venv/bin/python3", "manage.py"]
