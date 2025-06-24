import sqlite3
from config.settings import DB_PATH

def add_column_if_not_exists(cursor, table, column, definition):
    # カラム一覧を取得
    cursor.execute(f"PRAGMA table_info({table});")
    columns = [row[1] for row in cursor.fetchall()]
    # カラムがなければ追加
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition};")
        print(f"✅ カラム {column} を追加しました")
    else:
        print(f"✔️ カラム {column} はすでに存在します")

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # characters テーブルに必要なカラムを順次追加
        add_column_if_not_exists(cursor, "characters", "trait_scores", "TEXT")
        add_column_if_not_exists(cursor, "characters", "trait_selected", "INTEGER DEFAULT 0")
        add_column_if_not_exists(cursor, "characters", "pending_trait_selection", "INTEGER DEFAULT 0")
        add_column_if_not_exists(cursor, "characters", "trait_history", "TEXT")
        add_column_if_not_exists(cursor, "characters", "pending_trait_change", "INTEGER DEFAULT 0")

        conn.commit()
        print("✅ テーブル更新完了")

    except sqlite3.Error as e:
        print(f"❌ SQLiteエラー: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()

