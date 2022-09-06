########
# BASE #
########

FROM python:3.10-slim as base

ENV APP_NAME="sieve" \
    APP_ROOT="/sieve" \
    NON_ROOT_USER="sieve_user" \
    NON_ROOT_GROUP="sieve_group" \
    ENTRYPOINT_PATH="/sieve/docker/entry.sh" \
    CRONTAB="run_sieve" \
    CRONTAB_PATH="/var/spool/cron/crontabs/run_sieve" \
    CRONTAB_ENVIRONMENT="/etc/environment" \
    CRONTABS_BASE="/var/spool/cron/crontabs/" \
    \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_BINARY_PATH="/opt/poetry/bin/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$VENV_PATH/bin:$POETRY_HOME/bin:$PATH"

# install cron and set permissions
RUN apt-get update \
    && apt-get -y --no-install-recommends install cron \
    && apt-get clean \
    && chmod u+s /usr/sbin/cron \
    && touch /var/log/cron.log

# create non-root user
RUN addgroup --system $NON_ROOT_GROUP \
    && adduser --system --group $NON_ROOT_USER


###########
# Builder #
###########

FROM base as builder

RUN apt-get update \
    && apt-get -y --no-install-recommends install curl build-essential \
    && apt-get clean

ENV POETRY_VERSION=1.2.0
RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR $PYSETUP_PATH
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-dev


###############
# Development #
###############

FROM base as dev

ENV APP_ENV="dev" \
    LOG_LEVEL="DEBUG"

# install git for pre-commit hooks
RUN apt-get update \
    && apt-get -y --no-install-recommends install git \
    && apt-get clean

COPY --from=builder $POETRY_HOME $POETRY_HOME
COPY --from=builder $PYSETUP_PATH $PYSETUP_PATH

WORKDIR $PYSETUP_PATH
RUN poetry install

WORKDIR $APP_ROOT
COPY docker docker
COPY tasks tasks
COPY tests tests
COPY sieve sieve
COPY .flake8 .pre-commit-config.yaml pyproject.toml ./

# copy crontab and set non-root permissions
COPY docker/${CRONTAB} $CRONTABS_BASE
RUN chown -R $NON_ROOT_USER:$NON_ROOT_GROUP $CRONTABS_BASE $CRONTAB_ENVIRONMENT \
    && chmod +x $CRONTAB_PATH \
    && crontab -u $NON_ROOT_USER $CRONTAB_PATH

RUN chown -R $NON_ROOT_USER:$NON_ROOT_GROUP $APP_ROOT \
    && chmod +x $ENTRYPOINT_PATH $POETRY_BINARY_PATH

USER $NON_ROOT_USER

ENTRYPOINT [ "/sieve/docker/entry.sh" ]


##############
# Production #
##############

FROM base as prod

ENV APP_ENV="prod" \
    LOG_LEVEL="INFO"

COPY --from=builder $VENV_PATH $VENV_PATH

WORKDIR $APP_ROOT
COPY docker docker
COPY sieve sieve

# copy crontab and set non-root permissions
COPY docker/${CRONTAB} $CRONTABS_BASE
RUN chown -R $NON_ROOT_USER:$NON_ROOT_GROUP $CRONTABS_BASE $CRONTAB_ENVIRONMENT \
    && chmod +x $CRONTAB_PATH \
    && crontab -u $NON_ROOT_USER $CRONTAB_PATH

RUN chown -R $NON_ROOT_USER:$NON_ROOT_GROUP $APP_ROOT \
    && chmod +x $ENTRYPOINT_PATH

USER $NON_ROOT_USER

ENTRYPOINT [ "/sieve/docker/entry.sh" ]
