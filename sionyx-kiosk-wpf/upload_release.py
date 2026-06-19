import sys
import os
import requests
import datetime
import json

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

    db_url = os.environ.get("FIREBASE_DATABASE_URL")
    db_secret = os.environ.get("FIREBASE_DB_SECRET")
    github_token = os.environ.get("GITHUB_TOKEN")
    github_repo = "maxmax264/sionyx-releases"

    if not db_url or not db_secret:
        print("ERROR: Missing Firebase env vars")
        sys.exit(1)

    msi_name = f"sionyx-v{version}.msi"
    tag = f"v{version}"

    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    headers["Accept"] = "application/vnd.github+json"

    # Create GitHub Release
    print(f"[Upload] Creating GitHub Release {tag}...")
    release_resp = requests.post(
        f"https://api.github.com/repos/{github_repo}/releases",
        headers=headers,
        json={"tag_name": tag, "name": f"SIONYX {tag}", "body": f"Build {build_number}", "draft": False, "prerelease": False}
    )

    if release_resp.status_code == 422:
        # Release already exists - get it
        print(f"[Upload] Release {tag} already exists, fetching...")
        release_resp = requests.get(
            f"https://api.github.com/repos/{github_repo}/releases/tags/{tag}",
            headers=headers
        )

    if release_resp.status_code not in (200, 201):
        print(f"ERROR: Failed to create release ({release_resp.status_code}): {release_resp.text[:200]}")
        sys.exit(1)

    release_data = release_resp.json()
    upload_url = release_data["upload_url"].replace("{?name,label}", "")
    release_id = release_data["id"]

    # Upload MSI asset
    print(f"[Upload] Uploading {msi_name}...")
    with open(msi_path, 'rb') as f:
        msi_data = f.read()

    upload_headers = dict(headers)
    upload_headers["Content-Type"] = "application/octet-stream"

    asset_resp = requests.post(
        f"{upload_url}?name={msi_name}",
        headers=upload_headers,
        data=msi_data
    )

    if asset_resp.status_code not in (200, 201):
        print(f"ERROR: Asset upload failed ({asset_resp.status_code}): {asset_resp.text[:200]}")
        sys.exit(1)

    download_url = asset_resp.json()["browser_download_url"]
    print(f"[Upload] Asset uploaded: {download_url}")

    # Update Firebase DB via Render server
    update_data = {
        "version": version,
        "downloadUrl": download_url,
        "buildNumber": int(build_number),
        "releasedAt": datetime.datetime.utcnow().isoformat() + "Z"
    }

    admin_secret = os.environ.get("SIONYX_ADMIN_SECRET", "sionyx-admin-2026")
    db_resp = requests.post(
        "https://sionyx-auth-server.onrender.com/set-latest-version",
        json=update_data,
        headers={"x-sionyx-secret": admin_secret}
    )

    if db_resp.status_code != 200:
        print(f"ERROR: DB update failed ({db_resp.status_code}): {db_resp.text[:200]}")
        sys.exit(1)

    print(f"[Upload] Firebase DB updated: version={version}")
    print(f"[Upload] Done! Download URL: {download_url}")

if __name__ == "__main__":
    main()
