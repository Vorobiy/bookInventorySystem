import sqlite3


def connect():
    conn = sqlite3.connect("shopdata.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS book (
            id INTEGER PRIMARY KEY, 
            title TEXT, 
            author TEXT, 
            genre TEXT, 
            publication_date TEXT, 
            isbn TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert(title, author, genre, publication_date, isbn):
    conn = sqlite3.connect("shopdata.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO book VALUES (NULL, ?, ?, ?, ?, ?)", 
                (title, author, genre, publication_date, isbn))
    conn.commit()
    conn.close()


def view():
    conn = sqlite3.connect("shopdata.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM book")
    rows = cur.fetchall()
    conn.close()
    return rows


def search(title="", author="", genre="", publication_date="", isbn=""):
    conn = sqlite3.connect("shopdata.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM book WHERE 
        title LIKE ? AND 
        author LIKE ? AND 
        genre LIKE ? AND 
        publication_date LIKE ? AND 
        isbn LIKE ?
    """, (
        f"%{title}%" if title else "%", 
        f"%{author}%" if author else "%", 
        f"%{genre}%" if genre else "%", 
        f"%{publication_date}%" if publication_date else "%", 
        f"%{isbn}%" if isbn else "%"
    ))
    rows = cur.fetchall()
    conn.close()
    return rows


def delete(id):
    conn = sqlite3.connect("shopdata.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM book WHERE id=?", (id,))
    conn.commit()
    conn.close()


def update(id, title, author, genre, publication_date, isbn):
    conn = sqlite3.connect("shopdata.db")
    cur = conn.cursor()
    cur.execute("""
        UPDATE book SET 
        title=?, author=?, genre=?, publication_date=?, isbn=? 
        WHERE id=?
    """, (title, author, genre, publication_date, isbn, id))
    conn.commit()
    conn.close()

def reset_ids():
    conn = sqlite3.connect("shopdata.db")
    cur = conn.cursor()

    # Fetch all rows ordered by the current ID
    cur.execute("SELECT * FROM book ORDER BY id")
    rows = cur.fetchall()

    # Update IDs sequentially
    for new_id, row in enumerate(rows, start=1):
        cur.execute("UPDATE book SET id = ? WHERE id = ?", (new_id, row[0]))

    # Commit the changes
    conn.commit()
    conn.close()

def fetch_sorted_data(column):
    conn = sqlite3.connect("shopdata.db")
    cur = conn.cursor()
    query = f"SELECT * FROM book ORDER BY {column} COLLATE NOCASE"
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return rows
