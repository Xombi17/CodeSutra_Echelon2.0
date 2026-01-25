import sqlite3
import os

db_path = "silversentinel.db"
if not os.path.exists(db_path):
    print(f"File {db_path} does not exist in {os.getcwd()}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phase, strength FROM narratives LIMIT 10")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
