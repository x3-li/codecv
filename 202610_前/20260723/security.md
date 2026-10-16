| No | 杀毒软件名 | 是否支持 Ubuntu 24.04 | 是否支持 ARM64 | 是否需要 Cloud 集中管理 | DGX Spark 上使用推荐指数 |
|---:|---|---|---|---|---|
| 1 | Sophos Protection for Linux / Sophos EDR | ✅ 支持 | ✅ 支持 Linux ARM64，Kernel ≥ 5.3 | ✅ 基本需要 Sophos Central；可使用缓存/消息中继，但不是完全本地管理 | ★★★★☆ |
| 2 | Symantec Endpoint Security（SES） | ✅ 支持，但需核对 Agent 版本和内核 | ✅ 提供 Linux ARM64/AArch64 Agent；Ubuntu 24.04 ARM64 组合需厂商确认 | ⚠️ ARM64 通常需要 SES Cloud 管理；其他架构可有云端、本地或混合方案 | ★★★☆☆ |
| 3 | Microsoft Defender for Endpoint | ✅ 明确支持 Ubuntu 24.04 | ✅ 明确支持 Ubuntu 24.04 ARM64 | ✅ 需要 Microsoft Defender Portal；策略也可结合 Intune、脚本等管理 | ★★★★☆ |
| 4 | Fortinet FortiEDR | ✅ 支持 Ubuntu 24.04 x86_64 | ❌ 未确认支持 Linux ARM64 | ⚠️ 需要 FortiEDR Manager；可使用云端或本地管理方案 | ★☆☆☆☆ |
| 5 | CrowdStrike Falcon Prevent / Falcon Insight | ✅ 支持 | ⚠️ 支持 Ubuntu 24.04 ARM64，但官方主要以 AWS Graviton 分类，需要确认非 Graviton ARM64 | ✅ 主要通过 Falcon Cloud 集中管理 | ★★★★☆ |
| 6 | SentinelOne Singularity Endpoint | ✅ 支持范围需按当前 Agent 版本确认 | ⚠️ Linux ARM64 的公开支持范围不够清晰，必须向厂商确认 Ubuntu 24.04 ARM64 | ✅ 通常通过 SentinelOne 管理控制台；具体可用云端或私有部署方案需确认 | ★★☆☆☆ |
| 7 | Arctic Wolf Aurora Endpoint Security | ✅ 支持 Ubuntu 24.04 x86_64 | ❌ 当前公开 Linux 要求仍指向 x86_64；ARM64 支持主要是 Windows ARM64 | ✅ 依赖 Arctic Wolf Cloud 和 SOC 服务 | ★☆☆☆☆ |
| 8 | ReliaQuest GreyMatter | ➖ 不适用；不是安装在主机上的杀毒/EDR | ➖ 不适用 | ✅ GreyMatter 属于上层安全运营/MDR平台 | ☆☆☆☆☆ |
| 9 | SonicWall Capture Client | ✅ Linux 版本支持情况需核对具体版本 | ❌ Linux Agent 主要支持 x86_64；ARM 支持不包含 Linux EDR Agent | ✅ 通常需要 Capture Client Management Console / Cloud 管理 | ★☆☆☆☆ |
| 10 | Huntress Managed EDR for Linux | ✅ 明确支持 Ubuntu 24.04 | ✅ 明确支持 64-bit ARM Linux | ✅ 需要连接 Huntress Cloud 和 24×7 SOC；不适合离线环境 | ★★★☆☆ |
| 11 | Kaspersky Endpoint Security for Linux | ✅ 新版本支持 Ubuntu 24.04，需核对具体 KESL 版本 | ⚠️ 支持条件偏向 ARMv8-A；DGX Spark 为 ARMv9-A，且你们实际测试已出现不兼容 | ❌ 不强制 Cloud；可通过本地 Kaspersky Security Center 管理 | ★☆☆☆☆ |
| 12 | Trend Micro Vision One / Server & Workload Protection | ✅ 明确支持 Ubuntu 24.04 | ✅ Endpoint Sensor 明确支持 Ubuntu 24.04 ARM64；完整防护功能需确认 | ⚠️ Vision One 需要 Cloud；旧 Deep Security / 部分工作负载方案可有本地管理 | ★★★★☆ |
| 13 | Bitdefender GravityZone BEST for Linux | ✅ 明确支持 Ubuntu 24.04 | ✅ 支持 Linux ARM64，EDR Sensor 也有 ARM 支持 | ❌ 不强制 Cloud；GravityZone 有 Cloud 和 On-Premises 方案 | ★★★★★ |
| 14 | ESET Server Security / ESET Inspect | ✅ 支持 Ubuntu 24.04 | ❌ ESET 官方明确表示 Linux ARM 不支持 | ❌ 不强制 Cloud；ESET PROTECT 支持 Cloud 或 On-Premises | ★☆☆☆☆ |
| 15 | Cybereason EDR / NGAV | ✅ 官网列出 Ubuntu 24.04 | ⚠️ 未找到足够明确的通用 Linux ARM64 正式支持说明 | ✅ 通常依赖 Cybereason 管理平台；具体私有化部署需询问厂商 | ★★☆☆☆ |
| 16 | Palo Alto Networks Cortex XDR | ✅ 明确支持 Ubuntu 24.04 | ✅ 明确支持 Ubuntu 24.04 AArch64，并提供 ARM64 Kernel 支持列表 | ✅ 主要通过 Cortex XDR Cloud 管理控制台 | ★★★★★ |