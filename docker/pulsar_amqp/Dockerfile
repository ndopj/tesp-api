# Uses multi-stage builds requiring Docker 17.05 or higher
# See https://docs.docker.com/develop/develop-images/multistage-build/

# Environment variables and base image
FROM python:3.9-slim-buster as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$VENV_PATH/bin:$PATH"


# Builder is used to install shared depenedencies
FROM python-base as builder
WORKDIR $PYSETUP_PATH
RUN python -m venv $VENV_PATH && . .venv/bin/activate
RUN pip install kombu
RUN pip install 'pulsar-app'


# Development installs all dependencies and can be used
# to develope code.
FROM python-base as development
COPY --from=builder $PYSETUP_PATH $PYSETUP_PATH

# Pulsar is going to run docker commands and therefore it needs Docker
# CLI which will work with volume mapped Docker socket (i.e. DOFD)
# Copy Docker CLI from well known image where it is already installed.
# This does not integrate image in any way, it is used only to obtain CLI.
COPY --from=docker:dind /usr/local/bin/docker /usr/local/bin/

WORKDIR $PYSETUP_PATH
RUN pulsar-config
RUN pulsar-config --mq --force
EXPOSE 8913
ENTRYPOINT ["pulsar", "--mode", "webless"]
