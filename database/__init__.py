import sqlite3
import os
from dotenv import load_dotenv
import logging
import contextlib

load_dotenv()
logger = logging.getLogger(__name__)
DB_PATH = os.getenv("DB_PATH", "characters.db")

def init_db():
    try:
        with open_db_connection() as conn:
            with open(os.path.join(os.path.dirname(__file__), "schema.sql"), "r") as f:
                conn.executescript(f.read())
        logger.info("データベース初期化成功")
    except Exception as e:
        logger.error(f"DB初期化エラー: {e}")
        raise

@contextlib.contextmanager
def open_db_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()