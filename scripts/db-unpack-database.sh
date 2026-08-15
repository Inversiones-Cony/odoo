#!/usr/bin/env bash

set -euo pipefail

if [[ $# < 1 ]]; then
  echo "Error: Lacking parameters."
  exit 1
fi

DB_NAME=rikuras
DUMP_PATH="$1"
DB_SERVICE_NAME="${3:-db}"
POSTGRES_DB_USER="${POSTGRES_DB_USER:-postgres}"
ODOO_DB_USER="${5:-odoo}"

if [[ ! -v ODOO_USER_DB_PASSWORD ]]; then
  echo "Please make sure to pass the user and root password"
  exit -1
fi

read -r -p "This script will DROP the current database in order to restore the one you pass. Are you sure about this ? [N/y] " \
  answer

case "$answer" in 
  yes|y|Y|Yes)
    ;;
  *)
    echo "Aborting"
    exit 0
    ;;
esac

set -x


# Ensure the docker service is runnign
docker-compose up -d "$DB_SERVICE_NAME"

docker-compose exec --user "$POSTGRES_DB_USER" "$DB_SERVICE_NAME" \
  dropdb -U "$POSTGRES_DB_USER" --if-exists "$DB_NAME"

# Ensure this has user if brandnew:
docker compose exec --user "$POSTGRES_DB_USER" -T "$DB_SERVICE_NAME" \
    psql -U "$POSTGRES_DB_USER" -d postgres <<SQL
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_catalog.pg_roles
        WHERE rolname = '${ODOO_DB_USER}'
    ) THEN
        CREATE ROLE ${ODOO_DB_USER} LOGIN PASSWORD '${ODOO_USER_DB_PASSWORD}'
          NOSUPERUSER
          NOCREATEDB
          NOCREATEROLE;
    END IF;
END
\$\$;
SQL

docker-compose exec --user "$POSTGRES_DB_USER" "$DB_SERVICE_NAME" \
  createdb -U "$POSTGRES_DB_USER" "$DB_NAME"

# Create privileged extensions AS POSTGRES
docker-compose exec -T db psql -U $POSTGRES_DB_USER -d "$DB_NAME" \
  -c 'CREATE EXTENSION IF NOT EXISTS pg_trgm;'

echo "Restoring from ${DUMP_PATH}"
docker-compose exec -T "$DB_SERVICE_NAME" \
  pg_restore \
  -U "$POSTGRES_DB_USER" \
  -d "$DB_NAME" \
  --no-owner \
  --no-privileges \
  --role="$ODOO_DB_USER" \
  < "${DUMP_PATH}"


echo "Database restored"

