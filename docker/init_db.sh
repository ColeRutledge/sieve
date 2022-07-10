#! /bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
    CREATE DATABASE $DB_NAME WITH OWNER $DB_USER;
    GRANT ALL PRIVILEGES ON DATABASE $DB_NAME to $DB_USER;
    \c $DB_NAME $DB_USER;
    CREATE TABLE postings (
        id SERIAL PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        location VARCHAR(200) NOT NULL,
        company VARCHAR(200) NOT NULL,
        salary VARCHAR(200),
        date DATE NOT NULL,
        link TEXT NOT NULL,
        job_desc TEXT,
        tech VARCHAR(200) NOT NULL,
        source VARCHAR(200) NOT NULL);
    CREATE UNIQUE INDEX title_company ON postings (title, company);
EOSQL
