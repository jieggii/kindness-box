#!/usr/bin/bash

BACKUP_HOME="./.backups"
BACKUP_NAME="$(date "+%d.%m.%y-%H:%M:%S")"

echo "[*] Dumping mongo database..."
mongodump --host localhost \
  --port 27017 \
  --username "$(cat ./.secrets/mongo/username)" \
  --password "$(cat ./.secrets/mongo/password)" \
  --out "$BACKUP_HOME/$BACKUP_NAME"

cd "$BACKUP_HOME" || exit

echo "[*] Archiving the dump..."
tar -czvf "./$BACKUP_NAME.tar.gz" "./$BACKUP_NAME/"
rm -r "./${BACKUP_NAME:?}"

echo "[+] Done! backup stored at $BACKUP_HOME/$BACKUP_NAME.tar.gz."