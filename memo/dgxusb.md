# NVIDIA DGX Spark / Ubuntu 環境における USB ポート論理制御手順

## 1. 目的

本手順は、NVIDIA DGX Spark の Ubuntu / DGX OS 環境において、USB デバイスの利用を論理的に制御するためのものです。

通常時は USB デバイスを無効化し、USB メモリ、外付け HDD、USB SSD などを接続しても OS 側で利用できない状態にします。

利用が必要な場合のみ、管理者が一時的に対象 USB デバイスを許可し、利用後は再度無効化します。

---

## 2. 制御方針

本手順では `USBGuard` を使用します。

USBGuard により、USB デバイスの接続時に以下の制御を行います。

* 許可されていない USB デバイスは拒否する
* 一般ユーザーは USB デバイスを有効化できない
* 管理者のみ一時的に USB デバイスを許可できる
* 使用後は USB デバイスを再度拒否する

---

## 3. 前提条件

* OS は Ubuntu または NVIDIA DGX OS
* 管理者権限を持つユーザーで作業すること
* 可能であれば SSH 経由で作業すること
* USB キーボード、USB マウスを使用している場合は、誤って無効化しないよう注意すること

---

## 4. USBGuard のインストール

以下のコマンドを実行します。

```bash
sudo apt update
sudo apt install -y usbguard
```

インストール後、サービス状態を確認します。

```bash
systemctl status usbguard
```

---

## 5. 初期ポリシーの作成

現在接続されている USB デバイスを基準に、初期ポリシーを作成します。

事前に、許可したくない USB メモリ、外付け HDD、USB SSD などは取り外してください。

```bash
sudo sh -c 'usbguard generate-policy > /etc/usbguard/rules.conf'
sudo chmod 600 /etc/usbguard/rules.conf
sudo chown root:root /etc/usbguard/rules.conf
```

作成されたルールを確認します。

```bash
sudo cat /etc/usbguard/rules.conf
```

---

## 6. USBGuard の基本設定

設定ファイルを編集します。

```bash
sudo vi /etc/usbguard/usbguard-daemon.conf
```

以下の設定を確認、または追記します。

```ini
RuleFile=/etc/usbguard/rules.conf
ImplicitPolicyTarget=reject
PresentDevicePolicy=apply-policy
InsertedDevicePolicy=apply-policy
IPCAllowedUsers=root
```

### 設定内容

| 設定項目                                | 説明                          |
| ----------------------------------- | --------------------------- |
| `RuleFile`                          | USBGuard のルールファイル           |
| `ImplicitPolicyTarget=reject`       | ルールに存在しない USB デバイスを拒否       |
| `PresentDevicePolicy=apply-policy`  | 起動時に接続済みの USB デバイスにもポリシーを適用 |
| `InsertedDevicePolicy=apply-policy` | 新規接続された USB デバイスにもポリシーを適用   |
| `IPCAllowedUsers=root`              | USBGuard の操作を root のみに制限    |

---

## 7. USBGuard サービスの有効化

設定後、USBGuard を再起動します。

```bash
sudo systemctl restart usbguard
sudo systemctl enable usbguard
```

サービス状態を確認します。

```bash
sudo systemctl status usbguard
```

---

## 8. 通常時の状態確認

現在認識されている USB デバイスを確認します。

```bash
sudo usbguard list-devices
```

表示例：

```text
1: allow id 1d6b:0003 name "xHCI Host Controller"
2: block id 0781:5581 name "USB Storage" serial "1234567890"
```

`block` または `reject` になっている USB デバイスは、OS 上で使用できません。

---

## 9. USB デバイスを一時的に有効化する手順

### 9.1 USB デバイスを接続する

USB メモリ、外付け HDD、USB SSD などを接続します。

### 9.2 デバイス ID を確認する

```bash
sudo usbguard list-devices
```

表示例：

```text
23: block id 0781:5581 name "USB Storage" serial "1234567890"
```

この例では、デバイス番号は `23` です。

### 9.3 一時的に許可する

```bash
sudo usbguard allow-device 23
```

注意：

`-p` オプションは付けないでください。

```bash
sudo usbguard allow-device -p 23
```

上記のように `-p` を付けると、永続的な許可ルールとして保存される可能性があります。

---

## 10. USB デバイス使用後の無効化手順

### 10.1 マウント状態を確認する

```bash
lsblk
```

または：

```bash
mount | grep media
```

### 10.2 ファイルシステムをアンマウントする

例：

```bash
sudo umount /media/<user>/<mount_point>
```

または、デバイス名を指定してアンマウントします。

```bash
sudo umount /dev/sdX1
```

### 10.3 書き込み内容を同期する

```bash
sync
```

### 10.4 USB デバイスを再度拒否する

```bash
sudo usbguard list-devices
```

対象デバイス番号を確認します。

例：

```text
23: allow id 0781:5581 name "USB Storage" serial "1234567890"
```

以下を実行します。

```bash
sudo usbguard reject-device 23
```

これにより、対象 USB デバイスは接続されたままでも OS 上で使用できない状態になります。

---

## 11. 運用確認

USB デバイスを拒否した後、以下を確認します。

```bash
sudo usbguard list-devices
```

対象デバイスが `reject` または `block` 状態であることを確認します。

また、ディスクとして認識されていないことを確認します。

```bash
lsblk
```

対象 USB デバイスが表示されない、または利用できない状態であれば正常です。

---

## 12. 管理用スクリプトの作成

### 12.1 USB 状態確認スクリプト

```bash
sudo vi /usr/local/sbin/usb-status
```

以下を記載します。

```bash
#!/usr/bin/env bash
set -euo pipefail

usbguard list-devices
```

権限を設定します。

```bash
sudo chmod 750 /usr/local/sbin/usb-status
sudo chown root:root /usr/local/sbin/usb-status
```

実行例：

```bash
sudo /usr/local/sbin/usb-status
```

---

### 12.2 USB デバイス無効化スクリプト

```bash
sudo vi /usr/local/sbin/usb-reject
```

以下を記載します。

```bash
#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <usbguard-device-id>"
  exit 1
fi

DEVICE_ID="$1"

sync
usbguard reject-device "${DEVICE_ID}"
usbguard list-devices
```

権限を設定します。

```bash
sudo chmod 750 /usr/local/sbin/usb-reject
sudo chown root:root /usr/local/sbin/usb-reject
```

実行例：

```bash
sudo /usr/local/sbin/usb-reject 23
```

---

## 13. sudo 権限の制御

特定の運用担当者だけに USB 操作を許可する場合は、sudoers を設定します。

例として、`usbops` グループに所属するユーザーだけが USB 状態確認と拒否操作を実行できるようにします。

### 13.1 グループ作成

```bash
sudo groupadd usbops
```

### 13.2 ユーザー追加

```bash
sudo usermod -aG usbops <username>
```

### 13.3 sudoers 設定

```bash
sudo visudo
```

以下を追加します。

```sudoers
%usbops ALL=(root) NOPASSWD: /usr/bin/usbguard list-devices
%usbops ALL=(root) NOPASSWD: /usr/bin/usbguard allow-device *
%usbops ALL=(root) NOPASSWD: /usr/bin/usbguard reject-device *
%usbops ALL=(root) NOPASSWD: /usr/local/sbin/usb-status
%usbops ALL=(root) NOPASSWD: /usr/local/sbin/usb-reject *
```

注意：

本番環境では、`allow-device` の利用者を最小限に制限してください。

---

## 14. 動作テスト

### テスト 1：未許可 USB デバイスの接続

1. USB メモリを接続する
2. 以下を実行する

```bash
sudo usbguard list-devices
lsblk
```

期待結果：

* USBGuard 上で `block` または `reject` になる
* `lsblk` で利用可能なディスクとして表示されない
* 一般ユーザーがマウントできない

---

### テスト 2：一時許可

1. USB デバイス番号を確認する

```bash
sudo usbguard list-devices
```

2. 一時許可する

```bash
sudo usbguard allow-device <device_id>
```

3. ディスク認識を確認する

```bash
lsblk
```

期待結果：

* USB デバイスが一時的に利用可能になる

---

### テスト 3：使用後の拒否

1. アンマウントする

```bash
sudo umount /dev/sdX1
sync
```

2. USB デバイスを拒否する

```bash
sudo usbguard reject-device <device_id>
```

3. 状態を確認する

```bash
sudo usbguard list-devices
lsblk
```

期待結果：

* USB デバイスが使用不可になる
* 再接続しても自動的には利用できない

---

## 15. 注意事項

* USB キーボード、USB マウスを使用している場合、誤って拒否しないように注意してください。
* DGX Spark の USB Type-C ポートには電源用途のポートが含まれるため、物理的な電源制御ではなく、OS 側で USB デバイスの認可を制御します。
* `usb-storage` ドライバのブラックリスト化だけでは不十分です。
* USB デバイスはストレージ以外に、キーボード、ネットワークアダプタ、その他 HID デバイスとして振る舞う場合があります。
* 本番環境では、USBGuard のルールファイル `/etc/usbguard/rules.conf` を定期的に監査してください。

---

## 16. ロールバック手順

USBGuard により必要な USB デバイスが利用できなくなった場合は、管理者権限で以下を実行します。

```bash
sudo systemctl stop usbguard
```

恒久的に無効化する場合：

```bash
sudo systemctl disable usbguard
```

必要に応じて設定ファイルをバックアップします。

```bash
sudo cp /etc/usbguard/rules.conf /etc/usbguard/rules.conf.bak
sudo cp /etc/usbguard/usbguard-daemon.conf /etc/usbguard/usbguard-daemon.conf.bak
```

---

## 17. 運用ルール例

通常時：

```text
USB デバイスはすべて無効
```

利用前：

```text
管理者が対象 USB デバイスを確認し、一時的に allow-device を実行
```

利用後：

```text
アンマウント後、reject-device を実行
```

監査：

```text
定期的に /etc/usbguard/rules.conf と USBGuard の状態を確認
```

---

## 18. まとめ

本手順により、DGX Spark / Ubuntu 環境において USB デバイスを論理的に制御できます。

通常時は未許可の USB デバイスを拒否し、必要な場合のみ管理者が一時的に許可します。

利用後は再度拒否することで、USB メモリや外付け HDD を接続しても OS 上で利用できない状態を維持できます。
