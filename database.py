import sqlite3

def init_db():
    # Connects to the file. Creates it if it doesn't exist.
    conn = sqlite3.connect('data/patients.db')
    c = conn.cursor()
    # Create the table
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, name TEXT, thumbprint_id TEXT, history TEXT)''')
    conn.commit()
    conn.close()

def save_patient(name, thumb_id, history):
    conn = sqlite3.connect('data/patients.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (name, thumbprint_id, history) VALUES (?, ?, ?)", 
              (name, thumb_id, history))
    conn.commit()
    conn.close()