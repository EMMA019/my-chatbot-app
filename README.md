My Chatbot App – 成長するAIチャット

このプロジェクトは 会話を通じて成長するAIキャラクター と交流できるチャットアプリです。
ユーザーとのやり取りに応じて AI の性格や好感度が変化し、まるで生きているキャラクターのように成長します。

🧩 特徴

AIキャラクターの成長

会話や選択肢によって親密度（affection）や性格（trait）が変化

親密度に応じてAIの反応や性格が進化

イベント・分岐

trait や affection の値によって会話やイベントが変化

選択によって成長の方向性が変わる

自然な会話体験

外部 API（OpenAI 系）を利用し、AI が文脈を理解して返答

会話の履歴をもとに「覚えている」感覚を提供

簡単な育成要素

SQLite データベースでキャラクター情報・ステータスを保存

trait のスコアや好感度が可視化される設計も可能

🛠️ プロジェクト構成
app.py               - Flask メインアプリ
init_db.py           - データベース初期化
migrate_columns.py   - DB スキーマ変更管理
requirements.txt     - Python 依存パッケージ
templates/           - HTML テンプレート
database/            - DB 関連ファイル
services/            - 会話処理・成長ロジック
utils/               - ユーティリティ関数
config/              - 設定ファイル
characters.db        - キャラクターデータベース
mimiko-vertex-key.json - APIキー等認証情報

🚀 セットアップ手順

リポジトリのクローン

git clone https://github.com/EMMA019/my-chatbot-app.git
cd my-chatbot-app


仮想環境作成と依存関係インストール

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt


データベース初期化

python init_db.py


アプリケーション起動

python app.py


ブラウザで http://localhost:5000 にアクセスするとチャット画面が表示されます。
