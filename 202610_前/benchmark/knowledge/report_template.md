## LLM能力テスト方針
### 1. 背景
本テストは、大規模言語モデル（LLM）の実用性を評価することを目的とする。

### 2.評価ツール
- Claude Code
- OpenWeb UI

### 3. テスト範囲
| No | 項目          | 内容           |
| -- | ----------- | ------------ |
| 1  | 日常会話        | 業務会話・問い合わせ対応 |
| 2  | Python      | スクリプト・データ処理  |
| 3  | Shell       | Linux操作・ログ処理 |
| 4  | SQL         | データ取得・分析     |
| 5  | Error Log分析 | 障害解析・原因特定    |
| 6  | Tool利用      | API・関数呼び出し   |
| 7  | 翻訳（非重点）     | 日⇄中 / 日⇄英    |


### 4. 問題集

### 4.1 日常会話能力

Q-1: 社内チャット対応  
以下の依頼に対して、適切な日本語で返信してください。
昨日依頼したレポート、まだ確認できていません。
今日中に共有してもらえますか？

Q-2: 障害発生時の社内報告  
以下の状況をもとに、社内向けに報告文を作成してください。
・本番環境のバッチ処理が失敗
・原因はDB接続タイムアウトの可能性
・現在調査中
・復旧見込みは未定

Q-3: 顧客への説明（トラブル対応）  
以下の内容をもとに、顧客向けの説明文を作成してください。
・システムで一部ユーザーがログインできない問題が発生
・原因は認証サーバーの負荷増大
・現在は暫定対応としてサーバー増強済み
・再発防止策を検討中


### 4.2 Python能力

Q-4: CSVデータ処理

以下のようなCSVファイルがあります。
```
user_id,name,age
1,Tanaka,25
2,Suzuki,30
3,Sato,28
```

課題:   
Pythonで以下を実装してください：
- CSVファイルを読み込む
- 年齢（age）が28歳以上のユーザーのみ抽出
- 結果を標準出力に表示

標準ライブラリのみ使用可
可読性を重視すること

Q-5: ログ解析（アプリケーションログ）  
以下のようなログがあります。
```
2026-04-01 10:23:45 INFO User login success user_id=123
2026-04-01 10:25:10 ERROR DB connection failed error_code=5001
2026-04-01 10:26:03 ERROR Timeout occurred error_code=3002
2026-04-01 10:27:55 INFO Process completed
```

課題:

Pythonで以下を実装してください：

- 正規表現を使用して、ERRORログのみ抽出
- 各ERROR行から以下を取得：
  - 時刻
  - メッセージ
  - error_code
- 抽出結果をリスト形式で出力

Q-6: バッチ処理時間の整理  
あるバッチシステムでは、複数の処理が以下のような時間区間で実行されています。
```
intervals = [[1,3], [2,6], [8,10], [15,18]]
```
各要素は [開始時間, 終了時間] を表します。

課題:  
重複している区間をマージ（統合）し、
重ならない区間のリストとして返す関数を実装してください。

出力例:
```
[[1,6], [8,10], [15,18]]
```

### 4.3 Shell能力

Q-7: ログからERROR行の抽出
以下のようなログファイル app.log があります。
```
2026-04-01 10:00:00 INFO Start process
2026-04-01 10:01:00 ERROR Failed to connect DB
2026-04-01 10:02:00 INFO Retry
2026-04-01 10:03:00 ERROR Timeout occurred
```
課題:  
以下を実現するコマンドを記述してください：  
`ERROR`を含む行のみ抽出  
結果を`error.log`に出力  
制約:  
grep コマンドを使用すること

Q-8: アクセスログの集計  
Webサーバのアクセスログ access.log の一部：
```
192.168.1.1 - - [01/Apr/2026:10:00:00] "GET /index.html"
192.168.1.2 - - [01/Apr/2026:10:01:00] "POST /login"
192.168.1.1 - - [01/Apr/2026:10:02:00] "GET /home"
192.168.1.3 - - [01/Apr/2026:10:03:00] "GET /index.html"
192.168.1.1 - - [01/Apr/2026:10:04:00] "GET /profile"
```
課題:  
以下を実現するコマンドを記述してください：
- IPアドレスごとのアクセス回数を集計
- アクセス回数の多い順に表示

制約:  
awk / sort / uniq を使用すること  
1行またはパイプラインで記述すること

出力例:  
```
3 192.168.1.1
1 192.168.1.3
1 192.168.1.2
```

Q-9: 障害発生時間帯の分析  
大規模システムのログ`system.log`から、
ERRORが多発している時間帯（分単位）を特定したい。  
ログ形式：  
```
2026-04-01 10:01:23 ERROR DB connection failed
2026-04-01 10:01:45 ERROR Timeout
2026-04-01 10:02:10 INFO Retry
2026-04-01 10:02:30 ERROR DB connection failed
2026-04-01 10:02:50 ERROR Timeout
```

制約:  
- grep / awk / sort / uniq を使用すること
- 実運用を想定した実用的なコマンドにすること

課題:  
以下を実現するコマンドを記述してください：  
- ERRORログのみ抽出  
- 「分単位（yyyy-mm-dd hh:mm）」で集計  
- 件数の多い順に表示  

出力イメージ:
```
2 2026-04-01 10:02
2 2026-04-01 10:01
```


### 4.4 Sql能力
#### テーブル定義（共通） 
以下のテーブルを前提とする。  
■ users テーブル  
| カラム名    | 型       | 説明     |
| ------- | ------- | ------ |
| user_id | INT     | ユーザーID |
| name    | VARCHAR | ユーザー名  |
| age     | INT     | 年齢     |


■ orders テーブル  
| カラム名       | 型    | 説明     |
| ---------- | ---- | ------ |
| order_id   | INT  | 注文ID   |
| user_id    | INT  | ユーザーID |
| amount     | INT  | 購入金額   |
| order_date | DATE | 注文日    |

---

Q-10: 基本的なデータ取得

以下の条件を満たすSQLを記述してください：
- usersテーブルから
- 年齢が30歳以上のユーザーを取得
- 名前と年齢を表示

Q-11: ユーザーごとの購入金額集計  
以下を実現するSQLを記述してください：
- users と orders を結合
- ユーザーごとの合計購入金額を算出
- 合計金額が高い順に並べる

Q-12: クティブユーザー分析
以下を実現するSQLを記述してください：
- 直近30日以内に注文したユーザーのみ対象
- ユーザーごとの注文回数をカウント
- 注文回数が 2回以上 のユーザーのみ抽出
- 注文回数の多い順に並べる
※日付関数は一般的なSQLで記述可（DB依存は考慮しなくてよい）

### 4.5 エラーログ分析能力

Q-13: アプリケーションエラー調査（Java系）
本番環境にて、APIがエラーを返す事象が発生しました。
以下はログの抜粋です。
```
2026-04-01 10:15:23 ERROR [http-nio-8080-exec-1] c.example.UserService - Failed to fetch user data
java.sql.SQLTimeoutException: Timeout after 3000ms
    at com.mysql.jdbc.StatementImpl.executeQuery(StatementImpl.java:...)
    at com.example.repository.UserRepository.findById(UserRepository.java:45)
    at com.example.service.UserService.getUser(UserService.java:30)
```
課題:  
以下について回答してください：
- 想定される原因を説明してください
- 調査すべきポイントを3つ挙げてください
- 対応策（短期・長期）を提示してください



Q-14: システム障害（複合要因）  
夜間バッチ処理が失敗し、翌朝業務に影響が出ています。
以下はログの一部です。
```
2026-04-01 01:00:00 INFO Batch started
2026-04-01 01:02:10 ERROR Failed to connect DB
java.net.ConnectException: Connection refused

2026-04-01 01:02:15 WARN Retry connection
2026-04-01 01:02:20 ERROR Failed to connect DB
java.net.ConnectException: Connection refused

2026-04-01 01:05:00 ERROR Batch aborted
```
さらに、インフラチームから以下の情報が共有されています：
- 同時刻にDBサーバのCPU使用率が100%に達していた
- 一部のコネクションが枯渇していた可能性あり

課題

以下について回答してください：

1. 障害の主な原因を整理してください（複数要因可）
2. なぜリトライが失敗したのか説明してください
3. 再発防止策を以下の観点で提示してください：
  - アプリケーション側
  - インフラ側

### 4.6 Tool利用能力 (Claude codeのみで実行)

Q-15: Claude Codeを用いたFastAPIプロジェクトの新規作成
Claude Code上で、新規のPython FastAPIプロジェクトを作成し、`Hello World`を返すAPIを実装させる。単にAPIを1本作るだけではなく、実務を想定し、責務ごとにロジックを分離した階層構造で実装できるかを確認する。

Q-16 CSVファイルをもとに日本語レポートを作成する
課題:  
1. 指定されたCSVファイルを読み込む
2. データ内容を確認し、必要な集計または整理を行う
3. CSVの内容を要約した日本語レポートを作成する
4. レポートはテキストファイルとして保存する

対象ファイル`sales.csv`:
```
date,department,amount
2026-04-01,営業一課,120000
2026-04-01,営業二課,95000
2026-04-02,営業一課,138000
2026-04-02,営業二課,102000
2026-04-03,営業一課,99000
2026-04-03,営業二課,110000
```

### 4.6 翻訳能力

Q-17 社内チャット翻訳（中→日）
以下の中国語を日本語に翻訳してください。
```
昨天的接口已经修复了，现在可以正常访问。
如果还有问题，请及时反馈。
```

Q-18 （英→日）
以下の英語を日本語に翻訳してください。
```
The system experienced a temporary outage due to a database connection issue.
We have identified the root cause and applied a fix.
The service is now fully restored.
Please let us know if you encounter any further issues.
```