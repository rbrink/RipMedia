import os
import sqlite3

from utils import Logger

class RippingDatabase:
    def __init__(self, db_path="data/rips.db"):
        self.logger = Logger.get_logger(__name__)
        self.db_path = db_path
        dir_path = os.path.dirname(os.path.abspath(db_path))
        os.makedirs(dir_path, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discs (
                id INTEGER PRIMARY KEY,
                title TEXT,
                type TEXT,
                year TEXT,
                volume_label TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rips (
                id INTEGER PRIMARY KEY,
                disc_id INTEGER,
                title_index INTEGER,
                title_name TEXT,
                duration INTEGER,
                output_path TEXT,
                transcoded INTEGER DEFAULT 0,
                ripped_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(disc_id) REFERENCES discs(id)
            )
        """)
        self.conn.commit()

    def add_disc(self, title, media_type, year, volume_label, metadata=""):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO discs (title, type, year, volume_label, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (title, media_type, year, volume_label, metadata))
        self.conn.commit()
        return cursor.lastrowid

    def add_rip(self, disc_id, title_index, title_name, duration, output_path, transcoded=0):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO rips (disc_id, title_index, title_name, duration, output_path, transcoded)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (disc_id, title_index, title_name, duration, output_path, transcoded))
        self.conn.commit()

    def list_recent_rips(self, limit=25):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.title_name, d.title, r.output_path, r.ripped_at,
                   CASE r.transcoded WHEN 1 THEN 'Yes' ELSE 'No' END
            FROM rips r
            JOIN discs d ON r.disc_id = d.id
            ORDER BY r.ripped_at DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()

    def mark_transcoded(self, output_path):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE rips SET transcoded = 1 WHERE output_path = ?
        """, (output_path,))
        self.conn.commit()

    def close(self):
        self.conn.close()
