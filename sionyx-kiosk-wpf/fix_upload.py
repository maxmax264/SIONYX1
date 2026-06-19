content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\upload_release.py', encoding='utf-8').read()
old = '''    # Update Firebase DB
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
    print(f"[Upload] Done! Download URL: {download_url}")'''
new = '''    # Update Firebase DB via Render server
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
    print(f"[Upload] Done! Download URL: {download_url}")'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\upload_release.py', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
