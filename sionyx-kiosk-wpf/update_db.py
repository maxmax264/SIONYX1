import os, requests, datetime

version = "3.4.165"
build_number = "269"
download_url = "https://github.com/maxmax264/sionyx-releases/releases/download/v3.4.165/sionyx-v3.4.165.msi"

update_data = {
    "version": version,
    "downloadUrl": download_url,
    "buildNumber": int(build_number),
    "releasedAt": datetime.datetime.utcnow().isoformat() + "Z"
}

resp = requests.post(
    "https://sionyx-auth-server.onrender.com/set-latest-version",
    json=update_data,
    headers={"x-sionyx-secret": "sionyx-admin-2026"}
)
print(f"Status: {resp.status_code}")
print(resp.text[:300])
