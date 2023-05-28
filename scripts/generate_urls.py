#!/usr/bin/env python3
import json
import os
import sys
import uuid
repo_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(repo_folder)

from sqlitedb import SQLiteDB

"""
This scripts generates a 10000 uuid connections for tags.
"""
#############################################################################
tags = ['Vless-XTLS-reality'] #,'vmess-grpc'
quantity = 7000
db_path = f'{repo_folder}/db/database.db'
config_path = f"{repo_folder}/db/config.json"
domain = 'cdir-*.wlfvip.shop'
port = 443
##############################################################################

# Open the file
with open(f'{repo_folder}/scripts/base.json', 'r') as file:
    # Load the JSON data from the file
    data = json.load(file)
db = SQLiteDB(db_path)

for i in range(quantity):
    print(i)
    random_uuid = str(uuid.uuid4())
    client = {'email':f'{random_uuid}', 'id':  f'{random_uuid}' ,'password': f'{random_uuid}',"flow": "xtls-rprx-vision", 'level': 0}
    added = False
    for inbound in data['inbounds']:
        if 'listen' in inbound.keys() and inbound['listen'] in tags or 'tag' in inbound.keys() and inbound['tag'] in tags:
            inbound['settings']['clients'].append(client)
            added =True
    if added:
        db.add_entry(None, None, 1, random_uuid, domain, port, 0, None)

with open(config_path, "w") as outfile:
    json.dump(data, outfile, indent=4)