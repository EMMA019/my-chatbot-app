CREATE TABLE IF NOT EXISTS characters (
    name TEXT PRIMARY KEY,
    affection INTEGER DEFAULT 0,
    current_trait TEXT DEFAULT 'neutral',
    chat_count INTEGER DEFAULT 0,
    chat_last_update TEXT,
    triggered_events TEXT,
    self_name TEXT DEFAULT '私',
    speech_style TEXT DEFAULT '丁寧語'
);

CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_name TEXT NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    timestamp TEXT NOT NULL
);