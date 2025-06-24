import os
import asyncio
import logging
from datetime import datetime
from openai import OpenAI
from database.character import Character, save_character, update_affection
from services.prompt_builder import build_prompt, build_response_prompt
from services.trait_score_manager import update_trait_scores
from services.emotion_analyzer import analyze_emotion
from config.traits import trait_templates, trait_instructions
from services.event_manager import handle_trait_selection
from database.long_term_memory import save_long_term_memory
from database.long_term_memory import extract_memory_from_message


logger = logging.getLogger(__name__)

# OpenAIクライアントを初期化（APIキーは環境変数から）
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_openai_api(prompt):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return "（エラーが発生しました）"
    
def get_sweetness_level(affection: int) -> int:
    if affection < 30:
        return 1
    elif affection < 70:
        return 2
    else:
        return 3

def generate_chat_response(character, user_message, user_name="default_user"):
    """
    キャラクターとユーザーのチャットを処理し、応答を生成する。
    - 記憶抽出・保存
    - 感情分析
    - 性格スコア更新
    - 親愛度更新
    - 性格進化判定
    - GPT応答生成
    - テンプレ演出（甘さレベル）
    - キャラ保存
    """

    # ✅ 0. ユーザーメッセージから記憶抽出（#記憶, 覚えてて など）
    memories = extract_memory_from_message(user_message) or []
    for memory in memories:
        if isinstance(memory, tuple) and len(memory) == 2:
            topic, memory_text = memory
            if topic and memory_text:
                save_long_term_memory(character.name, user_name, topic, memory_text)


    # 1. 感情分析
    emotion_label, emotion_score = analyze_emotion(user_message)
    logger.info(f"🔍 感情分析: {emotion_label}（{emotion_score:.2f}）")

    # 2. 性格スコア更新
    update_trait_scores(character, emotion_label, emotion_score)

    # 3. 親愛度更新
    affection_info = update_affection(character.name, emotion_score, user_message)
    character.affection = int(affection_info["affection"])

    # 4. 性格進化ロジック
    logger.info(f"🔁 [before evolution] affection: {character.affection}, trait_selected: {character.trait_selected}")
    trait_event = handle_trait_selection(character)
    if trait_event:
        logger.info(f"✨ 性格イベント発生: {trait_event}")

    # 5. 使用性格を決定
    if character.trait_selected:
        pass  # current_trait を使用
    else:
        character.current_trait = "neutral"

    # 6. プロンプト生成
    prompt = build_prompt(
        user_message=user_message,
        character=character.to_dict(),
        trait_key=character.current_trait
    )

    # 7. GPT応答取得
    gpt_reply = call_openai_api(prompt)

    # 8. 甘さレベルに応じたテンプレ演出
    sweetness_level = get_sweetness_level(character.affection)
    styled_reply = build_response_prompt(
        character=character,
        raw_response=gpt_reply,
        trait_templates=trait_templates,
        sweetness_level=sweetness_level
    )

    # 9. キャラクター保存
    save_character(character)

    # 10. 応答と内部数値を返却
    return styled_reply, emotion_label, emotion_score, affection_info