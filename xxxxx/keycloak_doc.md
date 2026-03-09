Keycloak側の設定

下記の手順を実施した後、以下の情報を取得する必要があります。

Issuer URL

Realm 名

Client ID および Client Secret

JWK JSON ファイル

1. Realm の作成

（既存の Realm がある場合は、そのまま使用可能）

2. Client の作成

（既存の Client がある場合は、そのまま使用可能）

3. ユーザーの追加

以下のいずれかの方法でユーザーを追加します。

方法1：
Keycloak 上でユーザーを直接作成する。

方法2：
LDAP 連携を設定し、LDAP 上のユーザーを利用する。