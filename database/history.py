import sqlite3
from config.settings import DB_PATH
from datetime import datetime

def save_history(character_name, user_message, ai_response):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO history (character_name, user_message, ai_response, timestamp)
        VALUES (?, ?, ?, ?)
    """, (character_name, user_message, ai_response, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_history(character_name, limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_message, ai_response, timestamp 
        FROM history 
        WHERE character_name = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (character_name, limit))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_recent_history(character_name, limit=5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_message, ai_response 
        FROM history 
        WHERE character_name = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (character_name, limit))
    results = cursor.fetchall()
    conn.close()
    return results

