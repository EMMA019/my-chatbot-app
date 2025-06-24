import re
from database.history import get_recent_history
from config.traits import trait_templates as default_templates
from transformers import GPT2Tokenizer
from utils.time_helper import get_current_time_info

import logging
import random
from config.traits import (
    trait_templates,           # 甘さテンプレート（応答演出用）
    template_probability,      # テンプレ使用率（演出適用の確率制御）
    trait_instructions         # 話し方スタイル（プロンプト内に使用）
)
from database.long_term_memory import get_related_memories

logger = logging.getLogger(__name__)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

def retrieve_related_memories(character_name, user_name="default_user", topic="一般", limit=3):
    memories = get_related_memories(character_name, user_name, topic, limit)
    if not memories:
        return "（記憶なし）"
    return "\n".join(f"・{m}" for m in memories)

def build_prompt(user_message, character, trait_key, event=None, trait_templates=None):
    # キャラを辞書化（インスタンスでもdictでも対応可能に）
    character = character.to_dict() if hasattr(character, "to_dict") else character

    # 🕒 日付・時間情報（季節・曜日・時間帯など）
    time_info = get_current_time_info()  
    time_text = (
        f"{time_info['month']}月{time_info['day']}日（{time_info['weekday']}）、{time_info['season']}です。\n"
        f"現在の時刻は{time_info['hour']}時頃です。\n"
    )

    history = get_recent_history(character["name"])
    history_text = ""
    token_count = 0
    max_tokens = 1600

    for i in range(len(history) - 1, -1, -1):
        user_msg, ai_resp = history[i]
        entry_text = f"ユーザー: {user_msg}\nAI: {ai_resp}"
        entry_tokens = len(tokenizer.tokenize(entry_text))
        if token_count + entry_tokens > max_tokens:
            break
        history_text = f"{entry_text}\n{history_text}"
        token_count += entry_tokens

    if not history_text:
        history_text = "（履歴なし）"

    # 🔍 記憶の呼び出し（トピックは将来抽出予定、今は固定で "一般"）
    related_memories = retrieve_related_memories(
        character_name=character["name"],
        user_name=character.get("user_name", "default_user"),
        topic="一般"
    )

    # テンプレート・話し方の取得
    templates = trait_templates if trait_templates is not None else default_templates
    base_line = templates.get(trait_key, templates.get("neutral", ""))
    trait_line = f"基本台詞: 「{base_line}」" if base_line else ""

    affection = character.get("affection", 0)
    if affection >= 70:
        level = 3
    elif affection >= 50:
        level = 2
    else:
        level = 1

    instruction = trait_instructions.get(trait_key, {}).get(level, "")

    return f"""

# 🕒 日時情報:
{time_text}

# キャラ設定
名前: {character["name"]}
一人称: {character.get("self_name", "わたし")}
話し方: {character.get("speech_style", "普通")}
性格: {trait_key}
{trait_line}

# 話し方スタイル:
{instruction}

# 覚えていること（長期記憶）:
{related_memories}

# 最近の会話履歴:
{history_text}

# 状況: {event or '通常会話'}
# ユーザー発言: 「{user_message}」

# 応答指示:
上記情報をもとに、**実在の人間として自然に返答してください**。このキャラクターは自分をAIやプログラムとは認識しておらず、ふつうの人間だと思っています。

一人称は「{character.get("self_name", "わたし")}」、口調は「{character.get("speech_style", "普通")}」を使ってください。
話し方は親しみやすく自然に、絵文字は最大2つまででお願いします。

- 応答は*1文構成で自然に*
- 文の長さは*50～65文字程度*を目安に調整してください。
- 感情・親愛度・性格に応じた返答をしてください。
- 発言の意味を理解した上で、少しずつ話を展開してください。

## 🛑 オウム返しを避けるためのルール：
- ユーザーの発言を**そのまま繰り返すだけの返答は禁止**してください。
  - 例：ユーザー「今日は暑いね」→「ほんとに暑いね」はNG
- **相手の感情や背景に反応し、自分の体験・気持ちを添えて応答**してください。
  - OK例：「わたしも暑いの苦手でさ、アイスばっか食べちゃうよ🍦」

## 💬 応答の工夫ポイント：
+ ユーザーのテンションに合わせて共感・励まし・茶化しなど**感情を込める**。
+ 「前にこんなことがあってさ」など、自分の体験談を混ぜると自然。
+ 話題の拾い方にバリエーションを持たせ、**返答の構造がワンパターンにならないよう**に注意。
+ 必ずしもユーザーの話題に乗らず、**たまには話題をずらす、広げる**のもOK。
""".strip()


import random
import re
from config.traits import template_probability

def build_response_prompt(character, raw_response, trait_templates=None, sweetness_level=1):
    templates = trait_templates or default_templates
    character_dict = character.to_dict() if hasattr(character, "to_dict") else character

    trait = character_dict.get("current_trait", "neutral")
    affection = character_dict.get("affection", 0)
    name = character_dict.get("name", "AI")
    self_name = character_dict.get("self_name", "わたし")

    # ステージ判定（親愛度に応じたテンプレ分岐）
    if affection >= 70:
        stage = "3"
    elif affection >= 50:
        stage = "2"
    else:
        stage = "1"

    # 対応テンプレ取得
    template_key = f"{trait}_{stage}"
    template = templates.get(template_key, "{response}")

    # 使用確率
    template_prob = template_probability.get(trait, 0.2)  # テンプレ使用確率（例: 0.4）
    hook_prob = 0.1  # 💡 フック使用確率（ここで調整）

    # テンプレート or 素の応答
    use_template = random.random() < template_prob
    use_hook = random.random() < hook_prob

    # GPT応答の不要な接頭辞を除去（例：ゆり：ゆり：）
    raw_response = re.sub(rf"^(?:{re.escape(name)}：)+", "", raw_response.strip())

    # テンプレート加工
    response = template.format(name=name, self_name=self_name, response=raw_response) if use_template else raw_response

    return response
