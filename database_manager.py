import os
import sqlite3
from typing import List, Dict

# Store DB in the project directory so scripts run from any cwd
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "tunes.db")

def create_database():
    """Creates the table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tunes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            title TEXT,
            tune_type TEXT,
            meter TEXT,
            key_sig TEXT,
            content TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_tune(book_id: int, tune: Dict):
    """Inserts a single tune into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Use .get() to avoid errors if fields are missing in the ABC file
    title = tune.get('title', 'Unknown Title')
    tune_type = tune.get('type', 'Unknown')
    meter = tune.get('meter', '')
    key_sig = tune.get('key', '')
    content = tune.get('content', '')
    
    cursor.execute('''
        INSERT INTO tunes (book_id, title, tune_type, meter, key_sig, content)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (book_id, title, tune_type, meter, key_sig, content))
    
    conn.commit()
    conn.close()