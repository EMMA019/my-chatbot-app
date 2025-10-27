My Chatbot App

このプロジェクトは、Python と HTML を使用して構築されたシンプルなチャットボットアプリケーションです。ユーザーとの対話を通じて、指定されたキャラクターと会話ができます。

🛠️ 構成ファイルとディレクトリ

app.py：Flask アプリケーションのエントリーポイント。ルーティングとレスポンス処理を担当します。

init_db.py：データベースの初期化スクリプト。必要なテーブルの作成を行います。

migrate_columns.py：データベースのスキーマ変更を管理するマイグレーションスクリプト。

requirements.txt：プロジェクトで使用する Python パッケージの依存関係を記述しています。

templates/：HTML テンプレートを格納するディレクトリ。ユーザーインターフェースを構成します。

database/：データベース関連のファイルを格納するディレクトリ。

services/：外部 API との連携やビジネスロジックを担当するモジュールを格納します。

utils/：汎用的なユーティリティ関数を格納するモジュール。

config/：アプリケーションの設定ファイルを格納します。

mimiko-vertex-key.json：API キーなどの認証情報を含む JSON ファイル。

characters.db：SQLite データベースファイル。キャラクター情報を格納します。

🚀 セットアップ手順

リポジトリのクローン

git clone https://github.com/EMMA019/my-chatbot-app.git
cd my-chatbot-app


仮想環境の作成と依存関係のインストール

python -m venv venv
source venv/bin/activate  # Windows の場合は venv\Scripts\activate
pip install -r requirements.txt


データベースの初期化

python init_db.py


アプリケーションの起動

python app.py


ブラウザで http://localhost:5000 にアクセスすると、チャットボットアプリケーションが表示されます。

🔧 使用技術

バックエンド：Python 3.x、Flask

フロントエンド：HTML

データベース：SQLite

API 通信：JSON

🧩 今後の予定

ユーザーインターフェースの改善

多言語対応の実装

外部 API との連携強化

ユニットテストの追加

📄 ライセンス

このプロジェクトは MIT ライセンスのもとで公開されています。詳細は LICENSE
 をご覧ください。
