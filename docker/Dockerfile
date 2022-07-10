########
# BASE #
########

FROM python:3.10-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# install cron and set permissions
RUN apt-get update \
    && apt-get -y --no-install-recommends install cron \
    && apt-get clean \
    && chmod u+s /usr/sbin/cron \
    && touch /var/log/cron.log

ENV NON_ROOT_USER="sieve_user" \
    NON_ROOT_GROUP="sieve_group"

# create non-root user
RUN addgroup --system $NON_ROOT_GROUP
RUN adduser --system --group $NON_ROOT_USER


###########
# Builder #
###########

FROM base as builder

RUN apt-get -y --no-install-recommends install curl build-essential \
    && apt-get clean

ENV POETRY_VERSION=1.1.14
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

WORKDIR $PYSETUP_PATH
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-dev


###############
# Development #
###############

FROM base as dev

COPY --from=builder $POETRY_HOME $POETRY_HOME
COPY --from=builder $PYSETUP_PATH $PYSETUP_PATH

WORKDIR $PYSETUP_PATH
RUN poetry install

WORKDIR /sieve
COPY docker docker
COPY tasks tasks
COPY sieve sieve
COPY setup.cfg .

# copy crontab and set non-root permissions
COPY docker/run_sieve /var/spool/cron/crontabs/
RUN chown -R $NON_ROOT_USER:$NON_ROOT_GROUP /var/spool/cron/crontabs/ \
    && chmod +x /var/spool/cron/crontabs/run_sieve \
    && crontab -u $NON_ROOT_USER /var/spool/cron/crontabs/run_sieve

RUN chmod +x /sieve/docker/entry.sh

USER $NON_ROOT_USER

ENTRYPOINT [ "/sieve/docker/entry.sh" ]


##############
# Production #
##############

FROM base as prod

COPY --from=builder $VENV_PATH $VENV_PATH

WORKDIR /sieve
COPY docker docker
COPY sieve sieve

# copy crontab and set non-root permissions
COPY docker/run_sieve /var/spool/cron/crontabs/
RUN chown -R $NON_ROOT_USER:$NON_ROOT_GROUP /var/spool/cron/crontabs/ \
    && chmod +x /var/spool/cron/crontabs/run_sieve \
    && crontab -u $NON_ROOT_USER /var/spool/cron/crontabs/run_sieve

RUN chmod +x /sieve/docker/entry.sh

USER $NON_ROOT_USER

ENTRYPOINT [ "/sieve/docker/entry.sh" ]
