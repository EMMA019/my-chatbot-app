import sqlite3
from config.settings import DB_PATH

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # characters テーブル作成（personality カラムあり）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS characters (
        name TEXT PRIMARY KEY,
        personality TEXT,
        speech_style TEXT,
        self_name TEXT,
        age_group TEXT,  
        affection INTEGER DEFAULT 0,
        current_trait TEXT DEFAULT 'neutral',
        chat_count INTEGER DEFAULT 0,
        chat_last_update TEXT,
        last_chat_count INTEGER DEFAULT 0,
        triggered_events TEXT
    )
    """)

    # history テーブル作成
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_name TEXT NOT NULL,
        user_message TEXT NOT NULL,
        ai_response TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)

    # ✅ long_term_memory テーブルを追加 ←ここが新規
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS long_term_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_name TEXT NOT NULL,
        user_name TEXT,
        topic TEXT,
        memory TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # tag_options テーブル作成
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tag_options (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        option TEXT NOT NULL
    )
    """)

    # 初期データ投入
    initial_tags = [
        ("age", "学生"), ("age", "大学生"), ("age", "20代"), ("age", "お姉さん"),
        ("trait", "neutral"), ("trait", "dere"), ("trait", "tsundere"),
        ("trait", "yandere"), ("trait", "kuudere"), ("trait", "deredere"),
        ("speech_style", "敬語"), ("speech_style", "関西弁"),
        ("speech_style", "メスガキ"), ("speech_style", "フレンドリー"),
        ("self_name", "わたし"), ("self_name", "あたし"), ("self_name", "うち"),
        ("self_name", "ボク"), ("self_name", "あーし"),
        ("self_name", "わたくし"), ("self_name", "名前呼び")
    ]

    for category, option in initial_tags:
        cursor.execute("""
        INSERT INTO tag_options (category, option)
        SELECT ?, ? WHERE NOT EXISTS (
            SELECT 1 FROM tag_options WHERE category = ? AND option = ?
        )
        """, (category, option, category, option))

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了：すべてのテーブルを作成済")

if __name__ == "__main__":
    initialize_database()
