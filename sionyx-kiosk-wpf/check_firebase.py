import urllib.request, json
url = "https://pc-sion-default-rtdb.firebaseio.com/organizations/sionov/metadata/authDesign.json"
data = json.loads(urllib.request.urlopen(url).read())
print(f"formX={data.get('formX')}, formY={data.get('formY')}, formWidth={data.get('formWidth')}")
