以下は、**DGX Spark＝Ubuntu 24.04系、Linux ARM64／AArch64、NVIDIA GB10／ARMv9-A** を前提とした比較結果です。

> 推奨度は、各製品の総合的なセキュリティ性能ではなく、**DGX Spark上でアンチウイルス＋EDR製品として利用する場合の適合度**を示しています。
> Ubuntu 24.04およびARM64をサポートしている場合でも、DGX Sparkが正式認定されているとは限りません。


| No | セキュリティ製品名 | Ubuntu 24.04対応 | ARM64対応 | クラウド集中管理の要否 | DGX Sparkでの推奨度 |
|---:|---|---|---|---|---|
| 1 | Sophos Protection for Linux / Sophos EDR | ✅ 対応 | ✅ Linux ARM64対応、Kernel 5.3以上 | ✅ 基本的にSophos Centralが必要。キャッシュやメッセージリレーは利用可能だが、完全なオンプレミス管理ではない | ★★★★☆ |
| 2 | Symantec Endpoint Security（SES） | ✅ 対応。ただしAgentバージョンとKernelの確認が必要 | ✅ Linux ARM64／AArch64 Agentを提供。Ubuntu 24.04 ARM64の組み合わせはメーカー確認が必要 | ⚠️ ARM64端末は通常SES Cloudによる管理が必要。他アーキテクチャではクラウド、オンプレミス、ハイブリッド構成が可能 | ★★★☆☆ |
| 3 | Microsoft Defender for Endpoint | ✅ Ubuntu 24.04を正式サポート | ✅ Ubuntu 24.04 ARM64を正式サポート | ✅ Microsoft Defender Portalが必要。Intuneやスクリプトによるポリシー管理も可能 | ★★★★☆ |
| 4 | Fortinet FortiEDR | ✅ Ubuntu 24.04 x86_64をサポート | ❌ Linux ARM64の正式サポートは確認できない | ⚠️ FortiEDR Managerが必要。クラウド版またはオンプレミス版を利用可能 | ★☆☆☆☆ |
| 5 | CrowdStrike Falcon Prevent / Falcon Insight | ✅ 対応 | ⚠️ Ubuntu 24.04 ARM64をサポート。ただし公開資料では主にAWS Graviton向けとして記載されており、非Graviton環境は確認が必要 | ✅ 主にFalcon Cloudで集中管理 | ★★★★☆ |
| 6 | SentinelOne Singularity Endpoint | ✅ 現行Agentバージョンごとに確認が必要 | ⚠️ Linux ARM64の公開サポート範囲が不明確。Ubuntu 24.04 ARM64についてメーカー確認が必要 | ✅ 通常はSentinelOne管理コンソールを使用。クラウドまたはプライベート構成の詳細は確認が必要 | ★★☆☆☆ |
| 7 | Arctic Wolf Aurora Endpoint Security | ✅ Ubuntu 24.04 x86_64をサポート | ❌ 現在の公開Linux要件はx86_64向け。ARM64対応は主にWindows ARM64 | ✅ Arctic Wolf CloudおよびSOCサービスへの接続が必要 | ★☆☆☆☆ |
| 8 | ReliaQuest GreyMatter | ➖ 対象外。端末にインストールするアンチウイルス／EDR製品ではない | ➖ 対象外 | ✅ GreyMatterは上位層のセキュリティ運用／MDRプラットフォーム | ☆☆☆☆☆ |
| 9 | SonicWall Capture Client | ✅ Linux版は対応バージョンの確認が必要 | ❌ Linux Agentは主にx86_64向け。ARM対応にLinux EDR Agentは含まれない | ✅ 通常はCapture Client Management Consoleまたはクラウド管理が必要 | ★☆☆☆☆ |
| 10 | Huntress Managed EDR for Linux | ✅ Ubuntu 24.04を正式サポート | ✅ 64-bit ARM Linuxを正式サポート | ✅ Huntress Cloudおよび24時間365日のSOC接続が必要。オフライン環境には不向き | ★★★☆☆ |
| 11 | Kaspersky Endpoint Security for Linux | ✅ 新しいバージョンではUbuntu 24.04に対応。具体的なKESLバージョン確認が必要 | ⚠️ ARMv8-A中心のサポート。DGX SparkはARMv9-Aであり、実機検証でも互換性問題が発生済み | ❌ クラウドは必須ではない。オンプレミスのKaspersky Security Centerで管理可能 | ★☆☆☆☆ |
| 12 | Trend Micro Vision One / Server & Workload Protection | ✅ Ubuntu 24.04を正式サポート | ✅ Endpoint SensorはUbuntu 24.04 ARM64を正式サポート。完全な保護機能は確認が必要 | ⚠️ Vision Oneはクラウド管理が必要。旧Deep Securityや一部ワークロード製品はオンプレミス管理が可能 | ★★★★☆ |
| 13 | Bitdefender GravityZone BEST for Linux | ✅ Ubuntu 24.04を正式サポート | ✅ Linux ARM64をサポート。EDR SensorもARMに対応 | ❌ クラウド必須ではない。GravityZoneはCloud版とOn-Premises版を提供 | ★★★★★ |
| 14 | ESET Server Security / ESET Inspect | ✅ Ubuntu 24.04をサポート | ❌ ESETはLinux ARMを正式にサポートしていない | ❌ クラウド必須ではない。ESET PROTECTはCloud版とOn-Premises版を提供 | ★☆☆☆☆ |
| 15 | Cybereason EDR / NGAV | ✅ Ubuntu 24.04をサポート対象として掲載 | ⚠️ 一般的なLinux ARM64の正式サポートを示す明確な公開資料が不足 | ✅ 通常はCybereason管理プラットフォームが必要。プライベート環境への導入可否はメーカー確認が必要 | ★★☆☆☆ |
| 16 | Palo Alto Networks Cortex XDR | ✅ Ubuntu 24.04を正式サポート | ✅ Ubuntu 24.04 AArch64を正式サポート。ARM64向けKernel対応一覧も公開 | ✅ 主にCortex XDR Cloud管理コンソールを使用 | ★★★★★ |


## 簡易評価

| 分類                        | 製品                                                             |
| ------------------------- | -------------------------------------------------------------- |
| **優先的にPoCを実施すべき製品**       | Palo Alto Cortex XDR、Bitdefender GravityZone                   |
| **メーカー確認を優先すべき製品**        | Microsoft Defender for Endpoint、Sophos、CrowdStrike、Trend Micro |
| **ARM64対応だが制約が大きい製品**     | Symantec SES、Huntress                                          |
| **ARM64対応状況が不明確な製品**      | SentinelOne、Cybereason                                         |
| **基本的に候補から除外可能**          | Fortinet FortiEDR、Arctic Wolf、SonicWall、ESET                   |
| **実機検証により不適合と判断済み**       | Kaspersky                                                      |
| **端末向けアンチウイルス／EDRではない製品** | ReliaQuest                                                     |

## 推奨順位

1. **Palo Alto Cortex XDR**
2. **Bitdefender GravityZone**
3. **Microsoft Defender for Endpoint**
4. **Sophos**
5. **Trend Micro**
6. **CrowdStrike**
7. **Symantec Endpoint Security**
8. **Huntress**

最終選定前に、DGX Spark上で以下のコマンドを実行し、その結果をメーカーまたは代理店へ提示して、書面で互換性確認を取得する必要があります。

```bash
uname -m
uname -r
cat /etc/os-release
mokutil --sb-state
```

特に、以下の項目について確認が必要です。

* NVIDIAカスタムKernelへの対応
* ARMv9-AおよびNVIDIA GB10への対応
* Docker、CUDA、NVIDIA Driver、vLLMとの互換性
* モデル格納ディレクトリの除外設定
* Docker overlay2、データベース、大容量モデルファイルに対するリアルタイムスキャンの影響
* プロキシ、TLS Inspection、クラウド接続要件
