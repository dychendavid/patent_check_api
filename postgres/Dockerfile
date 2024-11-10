FROM postgres:14

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-contrib \
        postgresql-14-pgvector \
    && rm -rf /var/lib/apt/lists/*


COPY postgres/init-scripts/ /docker-entrypoint-initdb.d/
