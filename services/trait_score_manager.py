from database.character import save_character
from config.traits import trait_emotion_matrix

# スコア変化量の調整係数
SCALING_FACTOR = 1.4
THRESHOLD = 10  # スコア変化してもこの数値以下なら性格変化しない

def update_trait_scores(character, emotion_label, emotion_score):
    trait_scores = character.trait_scores or {}

    # 各性格にスコア加算
    for trait, coefficients in trait_emotion_matrix.items():
        coeff = coefficients.get(emotion_label, 0)
        delta = coeff * emotion_score * SCALING_FACTOR
        trait_scores[trait] = trait_scores.get(trait, 0) + delta

    # 現在のtraitと最も高いtraitが大きく乖離していたら更新
    dominant_trait = max(trait_scores, key=trait_scores.get)
    current_score = trait_scores.get(character.current_trait, 0)
    dominant_score = trait_scores[dominant_trait]

    if dominant_trait != character.current_trait and dominant_score - current_score > THRESHOLD:
        character.current_trait = dominant_trait

    # スコアとtraitを保存
    character.trait_scores = trait_scores
    save_character(character)