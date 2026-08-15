#!/usr/bin/env python

import sys

import odoo
from odoo.modules.neutralize import neutralize_database
from odoo.sql_db import db_connect
from odoo.tools import config
import os

config.parse_config(["-c", "odoo.conf"])
db_name = config["db_name"]

print("Just interested to see if we are getting the nvironment varaibles right")
print(f"We have the DBPASSWORD=:{os.environ.get('PGPASSWORD', 'Boop')}")
db = db_connect(db_name)

with db.cursor() as cr:
    cr.execute("""
        SELECT value
        FROM ir_config_parameter
        WHERE key='database.is_neutralized'
              """)
    row = cr.fetchone()
    if row and row[0].lower() in ("true","1"):
        print("Database is neutralized")
    else:
        print("Database is not neutralized")

# TODO: Ensure that when we call odoo the paramters that we pass in docker-compose.yaml are passed
