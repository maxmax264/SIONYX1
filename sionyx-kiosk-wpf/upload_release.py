import sys
import os
import requests
import datetime

def main():
    if len(sys.argv) < 4:
        print("Usage: upload_release.py <msi_path> <version> <build_number>")
        sys.exit(1)

    msi_path = sys.argv[1]
    version = sys.argv[2]
    build_number = sys.argv[3]

    if not os.path.exists(msi_path):
        print(f"ERROR: MSI not found: {msi_path}")
        sys.exit(1)

    storage_bucket = os.environ.get("FIREBASE_STORAGE_BUCKET")
    db_url = os.environ.get("FIREBASE_DATABASE_URL")
    db_secret = os.environ.get("FIREBASE_DB_SECRET")

    if not storage_bucket or not db_url or not db_secret:
        print("ERROR: Missing env vars")
        sys.exit(1)

    msi_name = os.path.basename(msi_path)
    storage_path = f"releases/{msi_name}"
    download_url = f"https://firebasestorage.googleapis.com/v0/b/{storage_bucket}/o/releases%2F{msi_name}?alt=media"

    print(f"[Upload] Uploading {msi_name} to Firebase Storage...")
    upload_url = f"https://firebasestorage.googleapis.com/v0/b/{storage_bucket}/o?uploadType=media&name={storage_path}"

    with open(msi_path, 'rb') as f:
        msi_data = f.read()

    resp = requests.post(
        upload_url,
        data=msi_data,
        headers={"Content-Type": "application/octet-stream"},
        params={"auth": db_secret}
    )

    if resp.status_code not in (200, 201):
        print(f"ERROR: Upload failed ({resp.status_code}): {resp.text[:200]}")
        sys.exit(1)

    print(f"[Upload] Upload complete")

    update_data = {
        "version": version,
        "downloadUrl": download_url,
        "buildNumber": int(build_number),
        "releasedAt": datetime.datetime.utcnow().isoformat() + "Z"
    }

    db_resp = requests.put(
        f"{db_url}/system/update.json?auth={db_secret}",
        json=update_data
    )

    if db_resp.status_code != 200:
        print(f"ERROR: DB update failed ({db_resp.status_code})")
        sys.exit(1)

    print(f"[Upload] Firebase DB updated: version={version}")
    print(f"[Upload] Done!")

if __name__ == "__main__":
    main()
