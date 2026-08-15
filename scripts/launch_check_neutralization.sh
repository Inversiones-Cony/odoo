#!/usr/bin/env bash

set -euo pipefail

if [[ ! -f "./odoo.conf" ]]; then 
  echo "./odoo.conf expected, but does not exist"
  exit 1
fi

DB_NAME="$(
python3 - <<'PY'
from odoo.tools import config

config.parse_config(['-c', './odoo.conf'])
print(config["db_name"])
PY
)" &> /dev/null

echo "Database name from config: $DB_NAME"
