print("✅ event_manager.py が読み込まれました")
def handle_trait_selection(character, threshold=5):
    print(f"🧪 [trait_selection] 呼び出し確認 → affection: {character.affection}, trait_selected: {character.trait_selected}")
    """
    Evolvian理論ベースの性格進化処理。

    親愛度が30以上かつ trait_selected=False の場合に以下を実行：
    - dominant_score - second_score ≥ threshold → 自動進化（性格固定）
    - それ未満 → ユーザーに性格を選ばせる（pending_trait_selection = True）

    この差分判定が「性格進化」の知的特徴（特許性の核）。
    """

    # ✅ すでに性格が決定されているなら終了
    if getattr(character, "trait_selected", False):
        print("🛑 trait_selected=True → スキップ")
        return None

    # ✅ 親愛度条件を満たしていなければ進化しない
    if not isinstance(character.affection, (int, float)) or character.affection < 30:
        print(f"🛑 親愛度が30未満（{character.affection}）→ スキップ")
        return None

    # ✅ スコアが未設定・空なら進化しない
    scores = getattr(character, "trait_scores", {})
    if not scores or len(scores) < 2:
        return None

    # ✅ スコア順にソート（高→低）
    sorted_traits = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    dominant_trait, dominant_score = sorted_traits[0]
    second_trait, second_score = sorted_traits[1]
    score_diff = dominant_score - second_score

    print(f"🧪 スコア差: {score_diff:.2f}（{dominant_trait} vs {second_trait}）/ affection: {character.affection}")

    if score_diff >= threshold:
        # ✅ 自動進化 → 固定・履歴追加
        character.current_trait = dominant_trait
        character.trait_selected = True
        character.pending_trait_selection = False
        if not hasattr(character, "trait_history"):
            character.trait_history = []
        character.trait_history.append(dominant_trait)
        return f"性格が『{dominant_trait}』に自動的に進化しました！"
    else:
        # ✅ プレイヤー選択モードへ
        character.pending_trait_selection = True
        return "性格を選んでください"
