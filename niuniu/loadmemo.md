# Load Balancerサービス構築手順

## 1. 環境準備

### 1.1 構成概要

* Windows 11 PC

  * Load Balancerサーバ兼Webサーバとして利用
  * WSL2（Ubuntu 24.04）導入済み
  * Docker導入済み
* DGX Spark × 2台

  * 非RoCE接続環境

---

## 2. Windowsサーバ作業

### 2.1 WSLの起動

PowerShellまたはコマンドプロンプトを起動し、以下のコマンドを実行する。

```bash
wsl -l -v
wsl -d <Ubuntuディストリビューション名>
```

---

### 2.2 Dockerイメージの取得（WSL環境）

LiteLLM、PostgreSQL、および Open WebUI のコンテナイメージを取得する。

```bash
# LiteLLM
docker pull litellm/litellm:v1.86.3

# PostgreSQL（LiteLLM用）
docker pull postgres:15

# Open WebUI
docker pull openwebui/open-webui:0.9.6
```

※ バージョンは作業時点の最新版を使用すること。

---

### 2.3 作業ディレクトリの作成（WSL環境）

```bash
mkdir -p /workspace/docker-app
```

---

### 2.4 Docker Composeファイルの配置

GitLabからDocker Compose関連ファイルを取得し、以下のディレクトリへ配置する。

```text
/workspace/docker-app
```

---

### 2.5 LiteLLMの起動

```bash
cd /workspace/docker-app/litellm
docker compose up -d
```

#### Load Balancing設定

`config.yaml` にて以下の設定を行う。

* 同一モデルに対して複数のエンドポイントを定義
* 各API Endpointには、それぞれのDGX Spark上のvLLMサーバIPアドレスを設定
* Routing Strategyは以下を指定

```yaml
routing_strategy: simple-shuffle
```

#### 管理画面へのアクセス

ブラウザから以下URLへアクセスする。

```text
http://localhost:9001/ui
```

ログインユーザーおよびパスワードは `docker-compose.yml` に設定された値を使用する。

---

### 2.6 LiteLLM動作確認

#### Playground動作確認

1. LiteLLM管理画面へログイン
2. Playgroundを開く
3. 対象モデルを選択
4. 複数回チャットを実行し、正常に応答が返却されることを確認

#### Load Balancing確認

LiteLLMのログを確認し、リクエストが各DGX Spark（vLLMサーバ）へ分散されていることを確認する。

複数のvLLMサーバへリクエストが振り分けられていることを確認できれば、Load Balancing設定は正常である。

---

### 2.7 Open WebUIの起動

```bash
cd /workspace/docker-app/openwebui
docker compose up -d
```

---

### 2.8 Open WebUI設定

ブラウザから以下URLへアクセスする。

```text
http://localhost:9000
```

ログイン情報は `docker-compose.yml` に設定された値を使用する。

管理者アカウントでログインすること。

---

#### 2.8.1 LiteLLM接続設定

以下のメニューからLiteLLM接続設定を行う。

```text
ユーザーアイコン
  └ 管理者設定
      └ 接続
```

設定項目：

* LiteLLM Host
* LiteLLM API Key

---

#### 2.8.2 モデル公開設定

以下の手順でモデルを公開する。

1. 「Models」メニューを選択
2. モデル一覧を表示
3. 利用対象モデルを「公開（Public）」に設定

---

#### 2.8.3 チャット動作確認

1. 新規チャットを作成
2. 公開したモデルを選択
3. AIとの対話が正常に実行できることを確認

以上で、Load Balancer環境およびOpen WebUI環境の構築は完了である。
