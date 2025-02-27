import sqlite3

class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, matter text, filename text, description text, location text)")
        self.conn.commit()

    def fetch_all(self):
        self.cur.execute("SELECT * FROM records")
        rows = self.cur.fetchall()
        return rows

    def get_record_by_id(self, id):
        self.cur.execute("SELECT * FROM records WHERE id=?", (id,))
        row = self.cur.fetchone()
        return row

    def insert(self, matter, file_name, description, location):
        self.cur.execute("INSERT INTO records VALUES (NULL, ?, ?, ?, ?)", (matter, file_name, description, location))
        self.conn.commit()

    def delete(self, id):
        self.cur.execute("DELETE FROM records where id=?", (id,))
        self.conn.commit()

    def update(self, id, matter, file_name, descripton, location):
        self.cur.execute("UPDATE records SET matter=?, filename=?, description=?, location=? WHERE id=?", (matter, file_name, descripton, location, id))
        self.conn.commit()

    def __del__(self):
        self.conn.close()