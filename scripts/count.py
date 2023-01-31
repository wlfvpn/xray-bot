#!/usr/bin/env python3
import sys
import os
repo_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(repo_folder)

from sqlitedb import SQLiteDB


db = SQLiteDB(f'{repo_folder}/db/database.db')
print(db.count_users_with_telegram_id())