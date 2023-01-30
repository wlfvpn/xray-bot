#!/usr/bin/env python3

from sqlitedb import SQLiteDB
db = SQLiteDB('db/database.db')
print(db.count_users_with_telegram_id())