#!/usr/bin/env python3
import json
import os
import sys
from tqdm import tqdm
import uuid
repo_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(repo_folder)

uuid = ''
from sqlitedb import SQLiteDB
db = SQLiteDB('/root/xray-bot/db/database.db')

print(db.get_username(uuid))