import sqlite3
import datetime
import os

class Database:
    def __init__(self, db_path="product_intelligence.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Updated schema for Brain v4.0
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                image_path TEXT,
                event_type TEXT,
                product_name TEXT,
                confidence FLOAT
            )
        ''')
        conn.commit()
        conn.close()

    def log_event(self, image_path, event_type, product_name, confidence):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO events (timestamp, image_path, event_type, product_name, confidence)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, image_path, event_type, product_name, confidence))
        conn.commit()
        conn.close()
        return timestamp

    def get_history(self, limit=20):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM events ORDER BY id DESC LIMIT ?', (limit,))
        history = cursor.fetchall()
        conn.close()
        return history
