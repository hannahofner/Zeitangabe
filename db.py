import sqlite3
import os

DB_NAME = 'app.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Initializes the database with users and favourites tables."""
    if not os.path.exists(DB_NAME):
        print("Creating new database...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table (Plain text password as requested for demo)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Create favourites table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favourites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            stop_id TEXT NOT NULL,
            stop_name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized.")

def create_user(username, password):
    """Creates a new user. Returns True if successful, False if username exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username, password):
    """Returns user dict if credentials match, else None."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

def get_user_by_id(user_id):
    """Returns user dict by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

def add_favourite(user_id, stop_id, stop_name):
    """Adds a favourite stop for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if already exists to avoid duplicates (optional but good)
    cursor.execute('SELECT * FROM favourites WHERE user_id = ? AND stop_id = ?', (user_id, stop_id))
    if cursor.fetchone():
        conn.close()
        return False # Already exists
        
    cursor.execute('INSERT INTO favourites (user_id, stop_id, stop_name) VALUES (?, ?, ?)', (user_id, stop_id, stop_name))
    conn.commit()
    conn.close()
    return True

def get_favourites(user_id):
    """Returns list of favourites for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM favourites WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def remove_favourite(fav_id, user_id):
    """Removes a favourite by ID, ensuring it belongs to the user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM favourites WHERE id = ? AND user_id = ?', (fav_id, user_id))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Run this file directly to init db
    init_db()
