import sys, os, requests, datetime

msi_path = r".\sionyx-installer-v3.4.165.msi"
version = "3.4.165"
build_number = "269"
github_token = os.environ.get("GITHUB_TOKEN")
github_repo = "maxmax264/sionyx-releases"
db_url = os.environ.get("FIREBASE_DATABASE_URL")
db_secret = os.environ.get("FIREBASE_DB_SECRET")
tag = f"v{version}"
msi_name = f"sionyx-v{version}.msi"

headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github+json"
}

# Delete existing release if any
print(f"[Upload] Creating GitHub Release {tag}...")
release_resp = requests.post(
    f"https://api.github.com/repos/{github_repo}/releases",
    headers=headers,
    json={"tag_name": tag, "name": f"SIONYX {tag}", "body": f"Build {build_number}", "draft": False, "prerelease": False}
)
print(f"Status: {release_resp.status_code}")
print(release_resp.text[:300])

if release_resp.status_code not in (200, 201):
    sys.exit(1)

release_data = release_resp.json()
upload_url = release_data["upload_url"].replace("{?name,label}", "")

print(f"[Upload] Uploading {msi_name}...")
with open(msi_path, "rb") as f:
    msi_data = f.read()

upload_headers = dict(headers)
upload_headers["Content-Type"] = "application/octet-stream"
asset_resp = requests.post(
    f"{upload_url}?name={msi_name}",
    headers=upload_headers,
    data=msi_data
)
print(f"Asset status: {asset_resp.status_code}")
if asset_resp.status_code not in (200, 201):
    print(asset_resp.text[:200])
    sys.exit(1)

download_url = asset_resp.json()["browser_download_url"]
print(f"[Upload] Done: {download_url}")

update_data = {
    "version": version,
    "downloadUrl": download_url,
    "buildNumber": int(build_number),
    "releasedAt": datetime.datetime.utcnow().isoformat() + "Z"
}
db_resp = requests.put(f"{db_url}/system/update.json?auth={db_secret}", json=update_data)
print(f"Firebase DB: {db_resp.status_code}")
