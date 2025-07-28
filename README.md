# DiscordVoiceVox

DiscordのメッセージをVOICEVOXなどの音声合成エンジンで読み上げるBOTです。

## 主な機能

- **テキストチャンネルのメッセージ読み上げ**
- **多様な音声合成エンジンに対応**
  - VOICEVOX
  - COEIROINK
  - SHAREVOX
  - A.I.VOICE
  - Aivis
- **声・速度・ピッチの個別設定**
- **辞書機能（単語登録）**
  - サーバーごとの辞書
  - グローバル辞書（管理者のみ）
  - ボイス辞書（音声ファイルでの登録）
- **サーバーごとの詳細設定**
  - 自動接続
  - 名前の読み上げ ON/OFF
  - 入退室メッセージの読み上げ ON/OFF
  - URLや絵文字の読み上げ設定
- **プレミアム機能**
  - Stripeと連携したプレミアムプランの提供
- **その他**
  - 緊急地震速報の通知機能

## 必要なもの

- **Python 3.8以上**
- **PostgreSQL**
- **各種音声合成エンジン** (VOICEVOX, COEIROINKなど)
- **Discord Bot Token**

## セットアップ手順

1.  **リポジトリをクローンします。**
    ```bash
    git clone https://github.com/lenlino/DiscordVoiceVox.git
    cd DiscordVoiceVox
    ```

2.  **必要なライブラリをインストールします。**
    ```bash
    pip install -r requirements.txt
    ```
    (現在 `requirements.txt` に問題があるため、正常にインストールできない可能性があります。)


3.  **設定ファイルを作成します。**
    `.env_temp` をコピーして `.env` という名前のファイルを作成し、お使いの環境に合わせて内容を編集してください。

    ```bash
    cp .env_temp .env
    ```

    **最低限必要な設定:**
    - `BOT_TOKEN`: あなたのDiscord Botのトークン
    - `VOICEVOX_HOST`: VOICEVOX APIのホストとポート (例: `127.0.0.1:50021`)
    - `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS`: PostgreSQLデータベースの接続情報

4.  **データベースをセットアップします。**
    Botを初めて起動すると、必要なテーブルが自動的に作成されます。

5.  **Botを起動します。**
    ```bash
    python main.py
    ```

## 使い方

`/vc` コマンドでBotをボイスチャンネルに接続すると、テキストチャンネルに投稿されたメッセージの読み上げが開始されます。

### 主なコマンド

- `/vc`: ボイスチャンネルへの接続・切断
- `/set`: 自分の声の種類・速度・ピッチを設定
- `/server-set`: サーバー全体の設定（自動接続、名前読み上げなど）
- `/adddict`: 辞書に単語を登録
- `/deletedict`: 辞書から単語を削除
- `/showdict`: 登録されている辞書の内容を表示

コマンドの詳細は、Discord上でスラッシュコマンドを入力すると確認できます。

## 注意事項

- A.I.VOICEの音声は、録音・配信での利用はできません。
- VOICEVOXの音声を利用して配信などを行う場合は、クレジット表記が必要です。詳しくは[VOICEVOXの利用規約](https://voicevox.hiroshiba.jp/term/)をご確認ください。

## ライセンス

[LICENSE](LICENSE) を参照してください。
