# LiteLLM + 2 台 vLLM によるローカル負荷分散構成案

## 1. 目的

本構成では、**1 台の通常 Linux VM + 2 台の DGX Spark** を利用して、ローカル環境で大規模言語モデルの Chat サービスを構築します。

主な目的は以下です。

* 外部に対して 1 つの統一 Chat API エンドポイントを提供する
* 2 台の DGX Spark を同時に推論サーバーとして利用する
* リクエストを 2 台の vLLM に自動分散する
* 片方の vLLM が停止しても、Chat サービスを継続利用できる
* RoCE は使用せず、マシン間のモデル並列も行わない
* シンプルで運用しやすい構成にする

---

## 2. 全体アーキテクチャ

```text
ユーザー / Chat UI / 業務システム
        |
        v
Linux VM
LiteLLM Proxy
統一 API 入口 + 負荷分散 + 障害時リトライ
        |
   -----------------
   |               |
   v               v
DGX Spark 1     DGX Spark 2
vLLM            vLLM
同一モデル       同一モデル
```

2 台の DGX Spark では、それぞれ独立して vLLM を起動し、同じモデルをロードします。

LiteLLM は通常の Linux VM 上に配置し、統一 API 入口および負荷分散コンポーネントとして利用します。

---

## 3. 基本設計

### 3.1 マシン間の分散推論は行わない

本構成では、1 つのモデルを 2 台の DGX Spark に分割して実行する構成は採用しません。

各 DGX Spark が、それぞれ完全なモデルを 1 つずつロードします。

```text
DGX Spark 1：完全なモデル + vLLM
DGX Spark 2：完全なモデル + vLLM
```

この方式のメリットは以下です。

* RoCE が不要
* DGX 間の高速インターコネクトに依存しない
* 片方の DGX に障害が発生しても、もう片方は独立して稼働できる
* 構成がシンプルで、保守しやすい

---

### 3.2 LiteLLM を統一入口として利用

クライアントは LiteLLM のみを呼び出します。

```text
http://<LiteLLM-VM-IP>:4000/v1/chat/completions
```

クライアント側は、バックエンドに何台の vLLM が存在するかを意識する必要はありません。

LiteLLM は以下の役割を担います。

* Chat リクエストの受付
* 負荷状況に応じた vLLM の選択
* リクエスト失敗時の自動リトライ
* 異常な vLLM ノードの一時的な切り離し
* 復旧後の vLLM ノードの再利用

---

## 4. 推奨ルーティング設定

最終的に以下の設定を推奨します。

```yaml
router_settings:
  routing_strategy: least-busy
  num_retries: 2
  timeout: 120
  allowed_fails: 2
  cooldown_time: 30
```

### パラメータ説明

| パラメータ              |          推奨値 | 役割                           |
| ------------------ | -----------: | ---------------------------- |
| `routing_strategy` | `least-busy` | 現在のリクエスト数が少ない vLLM に優先的に転送する |
| `num_retries`      |          `2` | 失敗時に最大 2 回までリトライする           |
| `timeout`          |        `120` | 1 回のリクエスト待機時間を最大 120 秒にする    |
| `allowed_fails`    |          `2` | 2 回失敗した vLLM を異常ノードとして扱う     |
| `cooldown_time`    |         `30` | 異常ノードへの転送を 30 秒間抑制する         |

`least-busy` を採用する理由は、LLM のリクエスト処理時間に大きな差があるためです。

短い質問は数秒で完了する一方、長いコンテキストや長文生成では数十秒かかる場合があります。
そのため、単純なラウンドロビンよりも、現在の処理数が少ない vLLM を選択する `least-busy` の方が、LLM 推論サービスには適しています。

---

## 5. LiteLLM 設定例

```yaml
model_list:
  - model_name: my-chat-model
    litellm_params:
      model: openai/my-chat-model
      api_base: http://10.0.0.11:8000/v1
      api_key: vllm-local-key
      timeout: 120

  - model_name: my-chat-model
    litellm_params:
      model: openai/my-chat-model
      api_base: http://10.0.0.12:8000/v1
      api_key: vllm-local-key
      timeout: 120

router_settings:
  routing_strategy: least-busy
  num_retries: 2
  timeout: 120
  allowed_fails: 2
  cooldown_time: 30
```

IP アドレスの例：

```text
10.0.0.11 = DGX Spark 1
10.0.0.12 = DGX Spark 2
```

2 台の vLLM では、同じモデル名を使用します。

```text
my-chat-model
```

---

## 6. 障害時の動作

通常時：

```text
リクエスト 1 -> DGX Spark 1
リクエスト 2 -> DGX Spark 2
リクエスト 3 -> 現在より空いている vLLM
```

DGX Spark 1 側の vLLM が停止した場合：

```text
リクエスト -> LiteLLM -> DGX Spark 1 -> 失敗
                        |
                        v
                      リトライ
                        |
                        v
                    DGX Spark 2 -> 成功
```

その後、LiteLLM は 30 秒間、異常ノードへのリクエスト転送を抑制します。

期待される効果：

* 片方の vLLM が停止しても、Chat サービスは継続利用可能
* 全体の処理能力は低下するが、サービスは停止しない
* 障害ノードが復旧すれば、再び負荷分散対象として利用可能

---

## 7. 本構成のメリット

| メリット          | 説明                                    |
| ------------- | ------------------------------------- |
| シンプルな構成       | Kubernetes や RoCE が不要                 |
| 可用性の向上        | 片方の vLLM が停止しても、もう片方でサービス継続可能         |
| 拡張しやすい        | DGX を追加する場合、LiteLLM に backend を追加するだけ |
| クライアント実装が簡単   | クライアントは 1 つの API エンドポイントのみを利用         |
| OpenAI API 互換 | 既存の Chat UI や SDK と接続しやすい             |
| 運用しやすい        | 各 DGX が独立して動作するため、障害範囲が明確             |

---

## 8. 注意点

本構成では、vLLM バックエンド側の冗長性は確保できます。

ただし、LiteLLM を配置する Linux VM は単一障害点になります。

第一段階では以下の構成を推奨します。

```text
1 台の LiteLLM VM + 2 台の DGX Spark vLLM
```

将来的に本番環境で入口部分の高可用性が必要な場合は、以下のような拡張構成を検討できます。

```text
Nginx / VIP
     |
LiteLLM 1 / LiteLLM 2
     |
DGX Spark 1 / DGX Spark 2
```

---

## 9. 結論

本提案では、**LiteLLM + 2 台の vLLM Replica** 構成を採用します。

最終構成は以下です。

```text
Client
  |
LiteLLM Proxy
  |
  |-- DGX Spark 1 vLLM
  |
  |-- DGX Spark 2 vLLM
```

推奨ルーティング設定：

```yaml
routing_strategy: least-busy
```

この構成により、RoCE を使用せず、マシン間のモデル並列も行わずに、ローカル大規模言語モデル Chat サービスの負荷分散と単一 vLLM 障害時の継続稼働を実現できます。

本構成は、顧客環境におけるローカル LLM サービスの第一段階の導入案として適しています。
