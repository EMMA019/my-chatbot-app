# ✅ app.py（最終統合版：デモ提出・実運用向け）

from flask import Flask, render_template, request, redirect, jsonify
import os
from dotenv import load_dotenv
from config.settings import DB_PATH
from database.character import (
    update_affection, get_character, save_character,
    get_tag_options, save_character_from_form
)
from database.history import save_history
from services.chat_service import generate_chat_response as get_ai_response
from database.long_term_memory import (
  save_long_term_memory,
  extract_memory_from_message, 
  get_related_memories,
  load_long_term_memories
)


load_dotenv()

if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"\u274c DBが存在しません：{DB_PATH}")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/character", methods=["GET"])
def character_page():
    return render_template("character.html",
        age_options=get_tag_options("age"),
        traits=get_tag_options("trait"),
        speech_styles=get_tag_options("speech_style"),
        self_names=get_tag_options("self_name")
    )

@app.route("/character", methods=["POST"])
def character_submit():
    character = save_character_from_form(request.form)
    if character is None:
        print("\u26a0\ufe0f キャラクター保存に失敗", dict(request.form))
        return "キャラクター保存に失敗しました。", 500
    return redirect(f"/chat/{character['name']}")

@app.route("/chat/<character_name>", methods=["POST"])
def chat_api(character_name):
    data = request.get_json()
    message = data.get("message", "")
    character = get_character(character_name)
    if character is None:
        return jsonify({"error": "キャラクターが見つかりません"}), 404

    # ✅ AI応答処理（親愛度等含む）
    reply, emotion_label, emotion_score, affection_info = get_ai_response(character, message)
    save_history(character_name, message, reply)

    # ✅ 記憶抽出と保存
    memories = extract_memory_from_message(message)
    for topic, memory_text in memories:
        if topic and memory_text:
            save_long_term_memory(character.name, "ユーザー", topic, memory_text)

    # ✅ ここで直近記憶を取得（UIに返す）
    memory_results = get_related_memories(character.name, "ユーザー", top_k=10, use_hashtag=False)
    hashtag_results = get_related_memories(character.name, "ユーザー", top_k=10, use_hashtag=True)

    return jsonify({
        "response": reply,
        "affection": affection_info["affection"],
        "trait": character.current_trait,
        "event": character.pending_trait_selection,
        "emotion": emotion_label,
        "emotion_score": emotion_score,
        "trait_scores": character.trait_scores,
        "pending_trait_selection": character.pending_trait_selection,
        "affection_delta": affection_info["delta"],
        "base_delta": affection_info["base_delta"],
        "phrase_bonus": affection_info["phrase_bonus"],
        "distance_factor": affection_info["distance_factor"],
        # ✅ 記憶をレスポンスに追加
        "memory_results": memory_results,
        "hashtag_results": hashtag_results
    })

@app.route("/chat/<character_name>", methods=["GET"])
def chat_page(character_name):
    character = get_character(character_name)
    if character is None:
        return "キャラクターが見つかりません。", 404
    return render_template("chatroom.html", character=character)

@app.route("/select_trait/<character_name>", methods=["POST"])
def select_trait(character_name):
    trait = request.json.get("trait")
    character = get_character(character_name)
    character.current_trait = trait
    character.trait_selected = True
    character.pending_trait_selection = False
    save_character(character)
    return jsonify({"new_trait": trait})


@app.route("/memory/<character_name>/<user_name>", methods=["GET"])
def get_memory(character_name, user_name):
    memories = load_long_term_memories(character_name, user_name)
    return jsonify({"memories": memories})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)