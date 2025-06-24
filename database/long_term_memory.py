import sqlite3
import re
from config.settings import DB_PATH
from datetime import datetime

def save_long_term_memory(character_name, user_name, topic, memory_text):
    """長期記憶を保存する（キャラ名・ユーザー名・トピック・内容）"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO long_term_memory (character_name, user_name, topic, memory, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (character_name, user_name, topic, memory_text, datetime.now()))

        conn.commit()
        print(f"🧠 記憶保存完了: {topic} - {memory_text}")
    except sqlite3.Error as e:
        print(f"❌ DB保存エラー: {e}")
    finally:
        conn.close()
# 修正後（top_k, use_hashtag に対応）
def get_related_memories(character_name, user_name=None, topic=None, top_k=5, use_hashtag=False):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = "SELECT memory FROM long_term_memory WHERE character_name = ?"
        params = [character_name]

        if user_name:
            query += " AND user_name = ?"
            params.append(user_name)

        if topic:
            query += " AND topic = ?"
            params.append(topic)

        if use_hashtag:
            query += " AND memory LIKE '#%'"

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(top_k)

        cursor.execute(query, params)
        results = [row[0] for row in cursor.fetchall()]
        return results

    except sqlite3.Error as e:
        print(f"❌ 長期記憶の取得エラー: {e}")
        return []
    finally:
        conn.close()      

def extract_memory_from_message(message: str):
    memories = []
    message = message.strip()

    # ✅ ハッシュタグ型
    hashtag_match = re.search(r"(#記憶|#覚えてて)\s*(.+)", message)
    if hashtag_match:
        topic = "一般"
        memory_text = hashtag_match.group(2).strip()
        if memory_text:
            memories.append((topic, memory_text))

    # ✅ 自然言語誘導型
    memory_triggers = [
        ("約束だよ", "約束"),
        ("絶対だよ", "約束"),
        ("覚えてて", "一般"),
        ("覚えといて", "一般"),
        ("忘れないで", "一般"),
        ("楽しみにしてる", "約束"),
        ("約束", "約束"),
        ("言ったからね", "約束")
    ]

    for trigger, topic in memory_triggers:
        if trigger in message:
            parts = message.split(trigger)
            memory_text = parts[0].strip()
            if not memory_text and len(parts) > 1:
                memory_text = parts[1].strip()
            if len(memory_text) < 2:
                memory_text = message.replace(trigger, "").strip()
            memory_text = re.sub(r"[。！!？?、,\s]*$", "", memory_text)
            if len(memory_text) >= 2:
                memories.append((topic, memory_text))
            break

    return memories

def load_long_term_memories(character_name, user_name):
    """指定キャラとユーザーの記憶をすべて取得"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT topic, memory FROM long_term_memory
            WHERE character_name = ? AND user_name = ?
            ORDER BY timestamp DESC
        """, (character_name, user_name))

        results = cursor.fetchall()
        return results

    except sqlite3.Error as e:
        print(f"❌ 記憶ロードエラー: {e}")
        return []

    finally:
        conn.close()

