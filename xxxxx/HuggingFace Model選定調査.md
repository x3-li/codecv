## HuggingFace Model選定調査

## 1. 前提

- GPUサーバ：Nvidia DGX Spark
- メモリ：CPU + GPU 共用 **128GB**
- 推論エンジン：**vLLM**

本調査では、HuggingFace 上で公開されている主要な LLM モデルについて、
 DGX Spark 環境で推論を実行する場合の **GPU メモリ使用量** を整理した。

## 2. HuggingFace 公式組織が公開しているモデル一覧

公式モデルの場合に必要となる GPU メモリ量は以下の通り。

| 所属組織   | Model          | weights precision | weights 使用GPUメモリ(GB) | KV Cache（単一ユーザー・16K context）(GB) | 合計(GB) |
| ---------- | -------------- | ----------------- | ------------------------- | ----------------------------------------- | -------- |
| meta-llama | Llama-3.1-8B   | FP16              | 16                        | 8                                         | > 24     |
|            | Llama-3.1-70B  | FP16              | 140                       | 40                                        | > 180    |
| openai     | gpt-oss-20b    | MXFP4             | 16                        | 12                                        | > 28     |
|            | gpt-oss-120b   | MXFP4             | 80                        | 65                                        | > 145    |
| google     | gemma-2-9b-it  | FP16              | 18                        | 10                                        | > 28     |
|            | gemma-3-27b-it | FP16              | 54                        | 22                                        | > 76     |

※KV Cache の概算式

KV Cache ≈
 2 × Transformer 層数 × Hidden size × コンテキスト長 × データ型サイズ（FP16 の場合：2 byte）

## 3.HuggingFace コミュニティによる量子化モデル

HuggingFace コミュニティでは、上記モデルを **量子化（Quantization）** した軽量版も公開されている。

| 所属組織       | Model                                | weights precision | weights size(GB) | KV Cache（単一ユーザー・16K context）(GB) | 合計(GB) |
| -------------- | ------------------------------------ | ----------------- | ---------------- | ----------------------------------------- | -------- |
| hugging-quants | Meta-Llama-3.1-8B-Instruct-AWQ-INT4  | INT4              | 5                | 8                                         | > 13     |
|                | Meta-Llama-3.1-70B-Instruct-AWQ-INT4 | INT4              | 40               | 40                                        | > 80     |
|                | gemma-2-9b-it-AWQ-INT4               | INT4              | 5                | 10                                        | > 15     |

量子化モデルを利用することで、**モデル weights のメモリ使用量を大幅に削減可能**。

## 4. 総合結論

# 4. 総合結論

DGX Spark（128GB メモリ）環境で LLM サービスを提供する場合、
 以下の点を考慮する必要がある。

- 小〜中規模モデル（8B〜20B程度）を利用する
- コンテキスト長（context length）を制御する
- 量子化モデル（INT4 / AWQ 等）を利用する
- 同時接続数（同時推論数）を制御する

これらを適切に管理することで、DGX Spark 環境でも **複数ユーザーによる LLM サービス提供が可能**となる。