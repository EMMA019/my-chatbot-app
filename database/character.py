import sqlite3
import random
from datetime import datetime, timedelta, timezone
from config.settings import DB_PATH
import logging
import math
import json

# ✅ ここが「先頭付近に追加する」コード！
print("🧪 character.py 参照中の DB_PATH →", DB_PATH)

logger = logging.getLogger(__name__)

PHRASE_SCORES = {
    "好き": 0.9,
    "愛してる": 1.2,
    "かっこいい": 0.7,
    "かわいい": 0.6,
    "すごい": 0.4,
    "尊敬": 0.8,
    "嫌い": -2.0,
    "うざい": -1.5,
    "ムカつく": -2.5,
    "死ね": -3.0,
    "キモい": -2.5
}

NEGATIVE_HISTORY_THRESHOLD = -0.5

def update_affection(name: str, emotion_score: float, user_message: str = "", history_scores: list = []) -> int:
    now = datetime.now(timezone.utc).astimezone()
    now_iso = now.isoformat()
    new_affection = 0
    distance_factor = 1.0

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT affection, chat_last_update, last_chat_count FROM characters WHERE name = ?", (name,))
        result = cursor.fetchone()

        if result:
            current_affection, last_update_str, chat_count = result
            if last_update_str:
                last_update = datetime.fromisoformat(str(last_update_str)).astimezone()
                time_diff = now - last_update
            else:
                time_diff = timedelta(days=100)
            chat_count = chat_count + 1 if time_diff < timedelta(minutes=30) else 1
        else:
            current_affection = 0
            chat_count = 1
            time_diff = timedelta(days=100)
            cursor.execute(
                "INSERT INTO characters (name, affection, chat_last_update, last_chat_count) VALUES (?, ?, ?, ?)",
                (name, current_affection, now_iso, chat_count)
            )

        # ✅ decayは無効化（放置による減少なし）
        decay = 0

        # ✅ 高親愛度でも上がりやすく
        distance_factor = 1.0 / (1 + math.exp(0.05 * (current_affection - 50)))

        # ✅ チャット連打ペナルティ（軽減）
        if chat_count > 3:
            distance_factor *= max(0.5, 1.0 - (chat_count * 0.1))

        # ✅ キーワードボーナス
        phrase_bonus = sum(round(score) for word, score in PHRASE_SCORES.items() if word in user_message)

        # ✅ ネガティブ履歴ペナルティ
        if history_scores:
            avg_score = sum(history_scores[-10:]) / min(10, len(history_scores))
            if avg_score < NEGATIVE_HISTORY_THRESHOLD:
                phrase_bonus -= 1

        # ✅ 長文ボーナス
        if len(user_message) >= 60:
            phrase_bonus += 1

        # ✅ 親愛度の変化幅を調整（上がりすぎ対策）
        base_delta = (emotion_score * 1.0) + random.uniform(-0.3, 0.6) + phrase_bonus

        # ✅ 上昇は最大 +3.0、下降は最大 -4.0 に制限
        if base_delta > 0:
            adjusted_delta = min(base_delta * distance_factor, 3.0)
        else:
            adjusted_delta = max(base_delta * distance_factor, -4.0)

        total_change = adjusted_delta - decay
        new_affection = max(0, min(round(current_affection + total_change), 100))

        cursor.execute(
            "UPDATE characters SET affection=?, chat_last_update=?, last_chat_count=? WHERE name=?",
            (new_affection, now_iso, chat_count, name)
        )
        conn.commit()

        logger.info(f"❤️ affection変動: {current_affection} → {new_affection} (Δ{new_affection - current_affection:.2f}, base:{base_delta:.2f}, phrase_bonus:{phrase_bonus}, factor:{distance_factor:.2f})")

    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        new_affection = current_affection if result else 0
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        if conn:
            conn.close()

    return {
    "affection": new_affection,
    "delta": new_affection - current_affection,
    "base_delta": base_delta,
    "phrase_bonus": phrase_bonus,
    "distance_factor": distance_factor,
    "chat_count": chat_count
}


def get_character(name: str) -> "Character":
    """キャラクターの情報をDBから取得してCharacterオブジェクトで返す"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM characters WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            data = dict(zip(columns, row))
            character = Character(name)
            character.load_from_dict(data)
            return character
        return None
    except sqlite3.Error as e:
        logger.error(f"Database error in get_character: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()


def update_trait(name: str, new_trait: str):
    """キャラクターの性格を更新する"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE characters SET personality=? WHERE name=?",
            (new_trait, name)
        )
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error in update_trait: {str(e)}")
    finally:
        if conn:
            conn.close()

def save_character_from_form(form) -> dict:
    """フォームからキャラクターを保存し、辞書で返す"""
    name = form.get("name")
    personality = form.get("trait")
    speech_style = form.get("speech_style")
    self_name = form.get("self_name")
    age_group = form.get("age")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO characters (
                name, personality, speech_style, self_name, age_group,
                affection, chat_count, trait_scores, current_trait,
                pending_trait_change, trait_history,
                trait_selected, pending_trait_selection
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            personality,
            speech_style,
            self_name,
            age_group,
            0,
            0,
            json.dumps({
                "deredere": 0,
                "tsundere": 0,
                "kuudere": 0,
                "yandere": 0
            }),
            "neutral",
            0,
            json.dumps([]),
            0,
            0
        ))
        conn.commit()

        return {
            "name": name,
            "personality": personality,
            "speech_style": speech_style,
            "self_name": self_name,
            "age_group": age_group
        }

    except sqlite3.Error as e:
        logger.error(f"Database error in save_character_from_form: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def get_tag_options(category: str) -> list:
    """タグカテゴリに応じた選択肢を返す"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT option FROM tag_options
            WHERE category = ?
        """, (category,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except sqlite3.Error as e:
        logger.error(f"Database error in get_tag_options: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def save_character(character):
    """キャラ情報を保存"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO characters (
                name, personality, speech_style, self_name, age_group,
                affection, chat_count, trait_scores, current_trait,
                pending_trait_change, trait_history,
                trait_selected, pending_trait_selection
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character.name,
            getattr(character, "personality", ""),
            getattr(character, "speech_style", ""),
            getattr(character, "self_name", ""),
            getattr(character, "age_group", ""),
            character.affection,
            character.chat_count,
            json.dumps(character.trait_scores),
            character.current_trait,
            int(getattr(character, "pending_trait_change", False)),
            json.dumps(getattr(character, "trait_history", [])),
            int(getattr(character, "trait_selected", False)),
            int(getattr(character, "pending_trait_selection", False))
        ))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error in save_character: {str(e)}")
    finally:
        if conn:
            conn.close()

class Character:
    def __init__(self, name):
        self.name = name
        self.affection = 0
        self.chat_count = 0
        self.trait_scores = {
            "deredere": 0,
            "tsundere": 0,
            "kuudere": 0,
            "yandere": 0
        }
        self.current_trait = "neutral"
        self.pending_trait_change = False
        self.trait_history = []
        self.trait_selected = False
        self.pending_trait_selection = False
        self.self_name = "わたし"

    def to_dict(self):
        return {
            "name": self.name,
            "affection": self.affection,
            "chat_count": self.chat_count,
            "trait_scores": json.dumps(self.trait_scores),
            "current_trait": self.current_trait,
            "pending_trait_change": int(self.pending_trait_change),
            "trait_history": json.dumps(self.trait_history),
            "trait_selected": int(self.trait_selected),
            "pending_trait_selection": int(self.pending_trait_selection),
            "self_name": self.self_name
        }

    def load_from_dict(self, data):
        self.affection = data.get("affection", 0)
        self.chat_count = data.get("chat_count", 0)

        raw_scores = data.get("trait_scores", self.trait_scores)
        if isinstance(raw_scores, str):
            try:
                self.trait_scores = json.loads(raw_scores)
            except json.JSONDecodeError:
                self.trait_scores = self.trait_scores
        else:
            self.trait_scores = raw_scores

        raw_history = data.get("trait_history", [])
        if isinstance(raw_history, str):
            try:
                self.trait_history = json.loads(raw_history)
            except json.JSONDecodeError:
                self.trait_history = []
        else:
            self.trait_history = raw_history

        self.current_trait = data.get("current_trait", "neutral")
        self.pending_trait_change = bool(data.get("pending_trait_change", False))
        self.trait_selected = bool(data.get("trait_selected", False))
        self.pending_trait_selection = bool(data.get("pending_trait_selection", False))
        self.self_name = data.get("self_name", "わたし")
