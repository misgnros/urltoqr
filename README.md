# urltoqr

URLを送ると2次元コード（QRコード）を返すSlackアプリ（Python製）

## 概要

2次元コードをお手軽に作成する方法はいまやいくらでもある。
ここで，少数のURLに対して2次元コードをつくりたい，またそれらを他人と簡単に共有したいとする。
はじめから大量に作成する場合であれば何かしらのスクリプトやアプリで一括作成し，クラウドにアップロードなどして共有すればよいが，少数だといちいち作成→アップロードして共有は面倒でもある。
そこで，URLを送ると2次元コードを返すSlackアプリ（Python製）をつくった。

使い方は2通り。
1. スラッシュコマンドでURLを送ると，アプリからDMで2次元コードが送られてくる。
2. チャンネル内でアプリをメンションしてURLを送ると，返信として2次元コードが送られてくる。

1つ目は他の人と共有しないパターン，2つ目は共有したいパターンを想定している。

## 環境

- Python 3.11以上
- Slackアプリの設定（Bot Token、Signing Secret）
- ngrokなどによるローカル環境の外部公開（HTTPモードの場合）

## セットアップ

### リポジトリのクローン

```bash
git clone https://github.com/misgnros/urltoqr
cd urltoqr
```

### 依存関係

下記にもとづいて各環境に適切なやり方でインストール。

- `qrcode>=8.2`: QRコード生成
- `slack-bolt>=1.26.0`: Slack Boltフレームワーク
- `slack-sdk>=3.37.0`: Slack SDK

### 環境変数の設定

以下の環境変数を設定する必要がある。

- `SLACK_BOT_TOKEN`: SlackアプリのBot User OAuth Token
- `SLACK_SIGNING_SECRET`: SlackアプリのSigning Secret
- `PORT`: アプリがリッスンするポート番号（オプション、デフォルト: 3000）

例：

```bash
export SLACK_BOT_TOKEN="xoxb-your-token"
export SLACK_SIGNING_SECRET="your-signing-secret"
export PORT=3000
```

### Slackアプリの設定

1. [Slack API](https://api.slack.com/apps)でアプリを作成
2. Bot Token Scopesに以下を追加：
   - `app_mentions:read`
   - `chat:write`
   - `commands`
   - `files:write`
   - `im:write`
3. スラッシュコマンド`/qr`を登録
4. Event Subscriptionsを有効化し、`app_mentions`イベントを購読
5. ngrokなどでローカル環境を公開し、Request URLを設定

### アプリの起動

```bash
python URLtoQR.py
```

## 使用方法

以下，URLは`http...`という文字列としている。それ以外の形式の文字列はURLではないと判断され，エラーメッセージが返ってくるようになっている。

### スラッシュコマンド

スラッシュコマンドを有効にしておき，コマンド`/qr`でURLを送る。

アプリからのDMで2次元コードが送られてくる。

### メンション

アプリをチャンネルに追加し，チャンネル内でアプリをメンションしてURLを送る。

スレッドでの返信として2次元コードが送られてくる。
