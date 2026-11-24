import json, os, re, urllib.request, datetime
KEY = os.environ["YOUTUBE_API_KEY"]
REGIONS = ["AR", "US", "MX", "ES"]
MAX_SEC = 240  # solo videos cortos
def dur(s):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s)
    h, mi, se = [int(x or 0) for x in m.groups()]
    return h*3600 + mi*60 + se
ids = []
for r in REGIONS:
    url = ("https://www.googleapis.com/youtube/v3/videos?part=contentDetails,status"
           f"&chart=mostPopular&regionCode={r}&maxResults=50&key={KEY}")
    data = json.load(urllib.request.urlopen(url))
    for v in data.get("items", []):
        if v["status"].get("embeddable") and dur(v["contentDetails"]["duration"]) <= MAX_SEC:
            if v["id"] not in ids: ids.append(v["id"])
if len(ids) < 15: print("pocos videos cortos, se mantiene lo anterior si hay"); 
if ids:
    json.dump({"updated": datetime.datetime.utcnow().isoformat(), "videos": ids},
              open("assets/videos.json", "w"))
print(len(ids), "videos")
