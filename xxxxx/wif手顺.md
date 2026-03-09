目的

本手順の目的は、GCP 外部の認証基盤（Keycloak）を利用して、Google Cloud の AI サービス（Vertex AI など）へ安全にアクセスする認証方式を構築することである。

従来の Service Account Key を使用した認証方式では、
長期的な認証情報（秘密鍵）の管理が必要となり、セキュリティリスクが高まる可能性がある。

本手順では Workload Identity Federation（WIF） を利用することで、

Service Account Key を使用しない認証方式を実現する

外部 Identity Provider（Keycloak）と GCP の認証連携を実現する

短期間のアクセストークンによる安全なリソースアクセスを実現する

ことを目的とする。

また、本構成により GCP 外部のアプリケーションやユーザーが Vertex AI などの GCP リソースを安全に利用できる環境を構築する。

