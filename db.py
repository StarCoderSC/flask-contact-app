import sqlite3

DB_NAME = "site.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT NOT NULL,
            message TEXT NOT NULL
            )
    ''')

    conn.commit()
    conn.close()

def save_message(name, message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO messages (name, message) VALUES (?, ?)", (name, message))
    conn.commit()
    conn.close()


def get_messages():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, message FROM messages ORDER BY id DESC")

    results = c.fetchall()
    conn.close()
    return results

def delete_message(message_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()

def get_message_by_id(message_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, message FROM messages WHERE id = ?", (message_id,))

    result = c.fetchone()
    conn.close()
    return result

def update_message(message_id, name, message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE messages SET name = ?, message = ? WHERE id = ?", (name, message, message_id))
    conn.commit()
    conn.close()

def create_post_table():
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts 
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


create_post_table()



