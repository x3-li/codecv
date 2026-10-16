# DGX Spark / Ubuntu 環境における USB 外付け HDD・SSD 利用制御手順

## 1. 目的

本手順は、NVIDIA DGX Spark の Ubuntu / DGX OS 環境において、USB 接続の外付け HDD、外付け SSD、USB メモリなどの USB ストレージデバイスを論理的に制御するためのものです。

通常時は USB ストレージデバイスを使用不可とし、管理者が必要な場合のみ一時的に有効化します。

利用後は、管理者が手動で再度無効化します。

---

## 2. 要件

本手順では、以下の運用を実現します。

| 要件     | 内容                              |
| ------ | ------------------------------- |
| 通常時    | USB HDD / SSD / USB メモリを使用不可にする |
| 管理者利用時 | 管理者が手動で一時的に有効化する                |
| 利用後    | 管理者が手動で無効化する                    |
| 再起動    | 初回設定時のみ必要                       |
| 日常運用   | HDD / SSD の利用前後で再起動しない          |

---

## 3. 制御方式

Linux カーネルモジュールの自動ロードを抑止します。

対象モジュールは以下の 2 つです。

| モジュール         | 役割                                                         |
| ------------- | ---------------------------------------------------------- |
| `usb-storage` | USB Mass Storage 用ドライバ。USB メモリ、外付け HDD などで使用される            |
| `uas`         | USB Attached SCSI 用ドライバ。USB 3.x の外付け SSD / HDD で使用されることが多い |

本手順では、`blacklist` により通常時の自動ロードを禁止します。

ただし、管理者が手動で一時的に有効化できるようにするため、以下のような設定は使用しません。

```conf
install usb-storage /bin/false
install uas /bin/false
```

この設定を入れると、管理者による手動 `modprobe` も失敗するため、本手順の要件には適しません。

---

## 4. 初回設定手順

### 4.1 対象モジュールの確認

以下を実行し、モジュールが存在することを確認します。

```bash
modinfo usb-storage
modinfo uas
```

正常な場合、各モジュールの情報が表示されます。

---

### 4.2 blacklist 設定ファイルの作成

以下のファイルを作成します。

```bash
sudo vi /etc/modprobe.d/disable-usb-storage.conf
```

以下を記載します。

```conf
blacklist usb-storage
blacklist uas
```

保存して終了します。

---

### 4.3 initramfs の更新

```bash
sudo update-initramfs -u
```

---

### 4.4 再起動

初回設定を反映するため、1 回だけ再起動します。

```bash
sudo reboot
```

---

## 5. 初回設定後の確認

再起動後、以下を実行します。

```bash
lsmod | grep -E 'usb_storage|uas'
```

期待結果：

```text
何も表示されない
```

何も表示されなければ、`usb-storage` および `uas` がロードされていない状態です。

次に、外付け HDD / SSD / USB メモリを接続し、ディスクとして認識されないことを確認します。

```bash
lsblk -o NAME,MODEL,SIZE,TRAN,TYPE,MOUNTPOINTS
```

期待結果：

```text
TRAN が usb の外付けディスクが表示されない
```

---

## 6. 管理者による一時有効化手順

USB HDD / SSD を利用する前に、管理者が以下を実行します。

```bash
sudo modprobe usb-storage
sudo modprobe uas
```

モジュールがロードされたことを確認します。

```bash
lsmod | grep -E 'usb_storage|uas'
```

表示例：

```text
uas                    32768  0
usb_storage            77824  1 uas
```

その後、外付け HDD / SSD / USB メモリを接続します。

ディスク認識を確認します。

```bash
lsblk -o NAME,MODEL,SIZE,TRAN,TYPE,MOUNTPOINTS
```

表示例：

```text
NAME   MODEL        SIZE TRAN TYPE MOUNTPOINTS
sdb    Samsung_T7   1.8T usb  disk
sdb1                1.8T usb  part /media/admin/T7
```

---

## 7. 管理者による無効化手順

利用後は、以下の順番で作業します。

### 7.1 USB ストレージの確認

```bash
lsblk -o NAME,MODEL,SIZE,TRAN,TYPE,MOUNTPOINTS
```

`TRAN` が `usb` のデバイスを確認します。

---

### 7.2 アンマウント

対象デバイスが `/dev/sdb1` の場合：

```bash
sudo umount /dev/sdb1
```

複数のパーティションがある場合は、すべてアンマウントします。

現在のマウント状態を確認する場合：

```bash
findmnt | grep /dev/sd
```

---

### 7.3 書き込みデータの同期

```bash
sync
```

---

### 7.4 外付け HDD / SSD を物理的に取り外す

アンマウントと `sync` 実行後、外付け HDD / SSD / USB メモリを取り外します。

---

### 7.5 USB ストレージモジュールのアンロード

```bash
sudo modprobe -r uas
sudo modprobe -r usb-storage
```

確認します。

```bash
lsmod | grep -E 'usb_storage|uas'
```

期待結果：

```text
何も表示されない
```

これで、USB ストレージデバイスは再び使用不可の状態になります。

---

## 8. 管理用スクリプトの作成

日常運用を簡単にするため、以下の 2 つのスクリプトを作成します。

| スクリプト                              | 用途                     |
| ---------------------------------- | ---------------------- |
| `/usr/local/sbin/usb-disk-enable`  | USB HDD / SSD を一時的に有効化 |
| `/usr/local/sbin/usb-disk-disable` | USB HDD / SSD を無効化     |

---

## 9. 有効化スクリプト

### 9.1 ファイル作成

```bash
sudo vi /usr/local/sbin/usb-disk-enable
```

以下を記載します。

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "[INFO] Enabling USB storage drivers..."

modprobe usb-storage
modprobe uas

echo "[INFO] Current USB storage modules:"
lsmod | grep -E '^(usb_storage|uas)\b' || true

echo "[OK] USB HDD/SSD can now be connected."
```

---

### 9.2 権限設定

```bash
sudo chmod 750 /usr/local/sbin/usb-disk-enable
sudo chown root:root /usr/local/sbin/usb-disk-enable
```

---

### 9.3 実行方法

```bash
sudo /usr/local/sbin/usb-disk-enable
```

実行後、外付け HDD / SSD / USB メモリを接続します。

---

## 10. 無効化スクリプト

### 10.1 ファイル作成

```bash
sudo vi /usr/local/sbin/usb-disk-disable
```

以下を記載します。

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "[INFO] USB storage devices:"
lsblk -o NAME,MODEL,SIZE,TRAN,TYPE,MOUNTPOINTS | awk 'NR==1 || $4=="usb"'

echo
echo "[WARN] Please make sure all USB HDD/SSD partitions are unmounted and physically unplugged."
echo "[WARN] If a USB disk is still mounted or in use, module removal will fail."
echo

sync

echo "[INFO] Removing USB storage drivers..."

modprobe -r uas || true
modprobe -r usb-storage || true

echo "[INFO] Current USB storage modules:"
if lsmod | grep -E '^(usb_storage|uas)\b'; then
  echo "[ERROR] USB storage modules are still loaded."
  echo "[ERROR] Please unmount all USB disks and unplug them, then run this command again."
  exit 1
else
  echo "[OK] USB HDD/SSD usage is disabled."
fi
```

---

### 10.2 権限設定

```bash
sudo chmod 750 /usr/local/sbin/usb-disk-disable
sudo chown root:root /usr/local/sbin/usb-disk-disable
```

---

### 10.3 実行方法

外付け HDD / SSD をアンマウントし、取り外した後に実行します。

```bash
sudo /usr/local/sbin/usb-disk-disable
```

---

## 11. sudo 権限の制御

特定の管理者だけが USB ストレージを有効化・無効化できるようにする場合は、専用グループを作成します。

### 11.1 グループ作成

```bash
sudo groupadd usbops
```

### 11.2 ユーザー追加

```bash
sudo usermod -aG usbops <username>
```

設定反映のため、対象ユーザーは再ログインしてください。

---

### 11.3 sudoers 設定

```bash
sudo visudo
```

以下を追加します。

```sudoers
%usbops ALL=(root) NOPASSWD: /usr/local/sbin/usb-disk-enable
%usbops ALL=(root) NOPASSWD: /usr/local/sbin/usb-disk-disable
%usbops ALL=(root) NOPASSWD: /usr/bin/lsblk
%usbops ALL=(root) NOPASSWD: /usr/bin/findmnt
```

これにより、`usbops` グループに所属するユーザーのみが USB HDD / SSD の有効化・無効化を実行できます。

---

## 12. 日常運用手順

### 12.1 通常時

通常時は、USB ストレージドライバがロードされていない状態にします。

確認コマンド：

```bash
lsmod | grep -E 'usb_storage|uas'
```

期待結果：

```text
何も表示されない
```

この状態では、USB HDD / SSD / USB メモリを接続しても、通常はディスクとして使用できません。

---

### 12.2 管理者が USB HDD / SSD を使用する場合

1. USB ストレージを一時的に有効化します。

```bash
sudo /usr/local/sbin/usb-disk-enable
```

2. 外付け HDD / SSD を接続します。

3. デバイスを確認します。

```bash
lsblk -o NAME,MODEL,SIZE,TRAN,TYPE,MOUNTPOINTS
```

4. 必要な作業を実施します。

---

### 12.3 使用後に USB HDD / SSD を無効化する場合

1. マウント状態を確認します。

```bash
lsblk -o NAME,MODEL,SIZE,TRAN,TYPE,MOUNTPOINTS
```

2. 対象パーティションをアンマウントします。

```bash
sudo umount /dev/sdX1
```

3. 書き込み内容を同期します。

```bash
sync
```

4. 外付け HDD / SSD を物理的に取り外します。

5. USB ストレージを無効化します。

```bash
sudo /usr/local/sbin/usb-disk-disable
```

6. モジュールがアンロードされていることを確認します。

```bash
lsmod | grep -E 'usb_storage|uas'
```

期待結果：

```text
何も表示されない
```

---

## 13. 動作確認テスト

### テスト 1：通常時に USB HDD / SSD が使えないこと

1. 以下を確認します。

```bash
lsmod | grep -E 'usb_storage|uas'
```

2. 外付け HDD / SSD を接続します。

3. 以下を確認します。

```bash
lsblk -o NAME,MODEL,SIZE,TRAN,TYPE,MOUNTPOINTS
```

期待結果：

```text
外付け USB HDD / SSD がディスクとして表示されない
```

---

### テスト 2：管理者が一時的に有効化できること

1. 以下を実行します。

```bash
sudo /usr/local/sbin/usb-disk-enable
```

2. 外付け HDD / SSD を接続します。

3. 以下を確認します。

```bash
lsblk -o NAME,MODEL,SIZE,TRAN,TYPE,MOUNTPOINTS
```

期待結果：

```text
TRAN が usb のディスクが表示される
```

---

### テスト 3：使用後に再度無効化できること

1. 対象デバイスをアンマウントします。

```bash
sudo umount /dev/sdX1
sync
```

2. 外付け HDD / SSD を取り外します。

3. 以下を実行します。

```bash
sudo /usr/local/sbin/usb-disk-disable
```

4. 以下を確認します。

```bash
lsmod | grep -E 'usb_storage|uas'
```

期待結果：

```text
何も表示されない
```

---

## 14. 注意事項

* 本手順は USB ストレージデバイスの利用を制御するものです。
* USB キーボード、USB マウス、USB LAN、USB カメラ、USB シリアルなどは対象外です。
* USB-C 電源ポートの給電には影響しません。
* すべての USB デバイスを禁止する方式ではありません。
* BadUSB や USB キーボード偽装などを防止する目的の場合は、USBGuard などの USB デバイス認可制御方式を検討してください。
* `modprobe -r` が失敗する場合、USB ストレージがまだマウント中、またはプロセスがアクセス中の可能性があります。
* 無効化前には必ずアンマウントと `sync` を実施してください。

---

## 15. ロールバック手順

USB ストレージ制御を解除する場合は、設定ファイルを削除またはリネームします。

```bash
sudo mv /etc/modprobe.d/disable-usb-storage.conf /etc/modprobe.d/disable-usb-storage.conf.bak
```

initramfs を更新します。

```bash
sudo update-initramfs -u
```

再起動します。

```bash
sudo reboot
```

再起動後、通常どおり USB HDD / SSD / USB メモリが自動認識される状態に戻ります。

---

## 16. まとめ

本手順により、DGX Spark / Ubuntu 環境で以下の運用が可能になります。

| 状態     | 内容                                   |
| ------ | ------------------------------------ |
| 通常時    | USB HDD / SSD / USB メモリは使用不可         |
| 管理者利用時 | 手動で `usb-storage` / `uas` をロードして一時利用 |
| 利用後    | アンマウント、取り外し後にモジュールをアンロード             |
| 再起動    | 初回設定時のみ必要                            |
| 日常運用   | USB HDD / SSD の利用前後で再起動不要            |

この方式は、USB ストレージだけを制御したい場合に適した軽量な運用方式です。
