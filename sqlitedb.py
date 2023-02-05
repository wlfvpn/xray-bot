import sqlite3
from datetime import datetime

class SQLiteDB:
    """
    SQLiteDB is a class that allows you to interact with a SQLite database using Python.
    It creates a table called 'users' with the following columns:
    telegram_id, telegram_username, enabled, date_created, uuid, server, port, usage, traffic_limit
    """

    def __init__(self, db_file):
        """
        Initializes the SQLiteDB class and creates the 'users' table if it does not already exist.
        
        Args:
            db_file (str): The file path for the SQLite database.
        """
        self.conn = sqlite3.connect(db_file)
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER, 
                    telegram_username TEXT, 
                    enabled INTEGER, 
                    date_created DATETIME, 
                    uuid TEXT, 
                    server TEXT, 
                    port INTEGER, 
                    usage INTEGER, 
                    traffic_limit INTEGER)''')
        self.conn.commit()
    
    def count_users_with_telegram_id(self):
        """
        Counts the number of entries in the 'users' table where telegram_id is not NULL.
        """
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE telegram_id IS NOT NULL")
        count = c.fetchone()[0]
        return count

    def add_entry(self, telegram_id, telegram_username, enabled, uuid, server, port, usage, traffic_limit):
        """
        Adds a new entry to the 'users' table.

        Args:
            telegram_id (int): The Telegram ID of the user.
            telegram_username (str): The Telegram username of the user.
            enabled (int): A flag indicating whether the user is enabled (1) or disabled (0).
            uuid (str): A unique identifier for the user.
            server (str): The server that the user is connected to.
            port (int): The port that the user is connected to.
            usage (int): The usage of the user.
            traffic_limit (int): The traffic_limit of the user.
        """
        c = self.conn.cursor()
        current_date = datetime.now().strftime('%Y-%m-%d')
        c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)", (telegram_id, telegram_username, enabled, current_date, uuid, server, port, usage, traffic_limit))
        self.conn.commit()

    def remove_entry(self, uuid):
        """
        Removes an entry from the 'users' table based on the provided uuid.

        Args:
            uuid (str): The unique identifier of the user to be removed.
        """
        c = self.conn.cursor()
        with self.conn:
            c.execute("DELETE FROM users WHERE uuid=?", (uuid,))
        self.conn.commit()
        
    def register_telegram_id(self, telegram_id, telegram_username, traffic_limit):
        """
        Registers a Telegram ID and username for a user, and updates the date_created and bandwidth_limit in the table. 
        
        Args:
            telegram_id (int): The Telegram ID of the user.
            telegram_username (str): The Telegram username of the user.
        bandwidth_limit (int): The bandwidth limit of the user.
        """

        c = self.conn.cursor()
        current_date = datetime.now().strftime('%Y-%m-%d')
        with self.conn:
            c.execute("UPDATE users SET telegram_id = ?, telegram_username = ?, date_created = ?, traffic_limit = ? WHERE telegram_id is NULL LIMIT 1", (telegram_id, telegram_username, current_date, traffic_limit))

    def get_uuid(self, telegram_id):
        """
        Retrieves the uuid of a user based on the provided Telegram ID.

        Args:
            telegram_id (int): The Telegram ID of the user.

        Returns:
            str: The uuid of the user, or None if no user was found with the provided Telegram ID.
        """
        c = self.conn.cursor()
        c.execute("SELECT uuid FROM users WHERE telegram_id=?", (telegram_id,))
        result = c.fetchone()
        if result:
            return result[0]
        else:
            return None
        
    def get_username(self, uuid):
        """
        Retrieves the telegram_username of a user based on the provided uuid.

        Args:
            uuid (str): The uuid of the user.

        Returns:
            str: The telegram username of the user, or None if no user was found with the provided Telegram ID.
        """
        c = self.conn.cursor()
        c.execute("SELECT telegram_id, telegram_username FROM users WHERE uuid=?", (uuid,))
        result = c.fetchone()
        if result:
            return result
        else:
            return None,None
        
    def get_usage(self, telegram_id):
        """
        Retrieves the usage of a user based on the provided telegram_id.

        Args:
            telegram_id (str): The telegram_id of the user.

        Returns:
            int: The usage of the user, or None if no user was found with the provided Telegram ID.
        """
        c = self.conn.cursor()
        c.execute("SELECT usage FROM users WHERE telegram_id=?", (telegram_id,))
        result = c.fetchone()
        if result:
            return result[0]
        else:
            return None

    def add_usage(self, uuid, amount):
        c = self.conn.cursor()
        with self.conn:
            c.execute("UPDATE users SET usage = usage + ? WHERE uuid = ?", (amount, uuid))
               
    def get_uuid_by_usage(self, traffic_limit):
        c = self.conn.cursor()
        c.execute("SELECT uuid FROM users WHERE usage > ?", (traffic_limit,))
        result = c.fetchall()
        return result
    def get_all_uuid(self):
        c = self.conn.cursor()
        c.execute("SELECT uuid FROM users")
        result = c.fetchall()
        return result
    
    def reset_usage(self):
        c = self.conn.cursor()
        with self.conn:
            c.execute("UPDATE users SET usage = 0")
    
if __name__=="__main__":
    table = SQLiteDB('database_test.db')
    for i in range(10):
        table.add_entry(None, None, 1, str(i), 'server1', 443, 0, None)

    table.register_telegram_id(98765, 'new_username',9999)
    table.register_telegram_id(9000, 'new_username2',9999)
    table.register_telegram_id(10200, 'new_username3',9999)


    uuid = table.get_uuid(12345)
    print(uuid)
    uuid = table.get_uuid(9000)
    print(uuid)
    print('count:',table.count_users_with_telegram_id())