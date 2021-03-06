# VERSION 2.0.0
# AUTHOR: sistemas@baobabsoluciones.es
# DESCRIPTION: Airflow 2.0 container based on puckel/docker-airflow https://github.com/puckel/docker-airflow by "Puckel_"

FROM python:3.8-slim-buster
LABEL maintainer="sistemas@baobabsoluciones"

# Never prompt the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

# Airflow vars
ARG AIRFLOW_VERSION=2.0.0
ARG AIRFLOW_USER_HOME=/usr/local/airflow
ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-2.0.0/constraints-3.8.txt"
ARG AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME}

# install Airflow requirements
RUN apt update -y && apt-get install -y --no-install-recommends \
		dos2unix \
        gcc \
		freetds-bin \
        krb5-user \
        ldap-utils \
        libffi6 \
        libffi-dev \
		libpq-dev \
        libsasl2-2 \
        libsasl2-modules \
        libssl1.1 \
        locales  \
        lsb-release \
		python3-dev \
        sasl2-bin \
        sqlite3 \
        unixodbc

# install Airflow and extras: celery,postgres and redis
RUN pip install "apache-airflow[celery,postgres,redis]==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

# copy init script and config to container
COPY scripts/initairflow.sh /initairflow.sh

RUN useradd -ms /bin/bash -d ${AIRFLOW_USER_HOME} airflow
RUN chown -R airflow: /usr/local/airflow

RUN dos2unix /initairflow.sh
RUN chmod +x /initairflow.sh

EXPOSE 8080 5555 8793

USER airflow
WORKDIR ${AIRFLOW_USER_HOME}
ENTRYPOINT ["/initairflow.sh"]
CMD ["webserver"]