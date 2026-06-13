import urllib.request, json

url = "https://pc-sion-default-rtdb.firebaseio.com/organizations/sionov/users/PbxxiK4lGXZu1kIl6zd2dll6faC2.json"
with urllib.request.urlopen(url) as r:
    data = json.loads(r.read())
    print(json.dumps(data, indent=2, ensure_ascii=False))
