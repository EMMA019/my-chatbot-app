from google.cloud import language_v1
import os
import logging

logger = logging.getLogger(__name__)

def classify_emotion(score, magnitude):
    """
    Vertex AIのscore/magnitudeから6分類するルールベース分類器。
    - score: -1.0 ～ +1.0（ポジ⇄ネガ）
    - magnitude: 感情の強さ（0.0～）
    """
    if magnitude < 0.2:
        return "neutral"
    elif score >= 0.6:
        return "joy"
    elif score >= 0.3:
        return "surprise"
    elif score <= -0.6:
        return "anger"
    elif score <= -0.3:
        return "fear"
    elif score < 0:
        return "sadness"
    else:
        return "neutral"

def analyze_emotion(text):
    if not text.strip():
        return "neutral", 0.0

    try:
        client = language_v1.LanguageServiceClient()

        document = language_v1.Document(
            content=text[:1000],  # 長すぎる文を防ぐ
            type_=language_v1.Document.Type.PLAIN_TEXT,
            language="ja",
        )

        response = client.analyze_sentiment(request={"document": document})
        sentiment = response.document_sentiment
        score = round(sentiment.score, 4)
        magnitude = round(sentiment.magnitude, 4)

        emotion_label = classify_emotion(score, magnitude)

        logger.info(f"[Vertex感情分析] テキスト:「{text}」→ 感情: {emotion_label}, score: {score}, magnitude: {magnitude}")
        return emotion_label, magnitude  # 感情と強度を返す

    except Exception as e:
        logger.error(f"[Vertex感情分析エラー] {e}")
        return "neutral", 0.0

