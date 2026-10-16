
### 開発者作業サポート

#### GHSA-673q-mjm6-r5xrとGHSA-p3m5-59mp-jv5r
使用している Next.js 16.2.4 は脆弱性の対象バージョンに該当する。
ただし、LiteLLM v1.86.3 の Admin UI は output: "export" により Static Export としてビルドされており、実行環境では Next.js Runtime Server は動作しない。
当該脆弱性の成立条件となる Server Actions / Server Functions 等のサーバー機能は使用されないため、影響なしと判断する。

#### GHSA-xqc2-xf4c-x3h3とGHSA-h3gv-c5rc-p453
当該脆弱性は React Server Components の react-server-dom-* 19.x を対象としている。
LiteLLM v1.86.3 は React 18.3.1 を使用しており、対象となる react-server-dom-webpack、react-server-dom-turbopack、react-server-dom-parcel は依存関係に含まれていない。
したがって、影響なしと判断する。