import json, os, re, urllib.request, datetime
KEY = os.environ["YOUTUBE_API_KEY"]
REGIONS = ["AR", "US", "MX", "ES"]
MAX_SEC = 240
def dur(s):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s)
    h, mi, se = [int(x or 0) for x in m.groups()]
    return h*3600 + mi*60 + se
items, seen = [], set()
for r in REGIONS:
    url = ("https://www.googleapis.com/youtube/v3/videos?part=contentDetails,status"
           f"&chart=mostPopular&regionCode={r}&maxResults=50&key={KEY}")
    data = json.load(urllib.request.urlopen(url))
    for v in data.get("items", []):
        d = dur(v["contentDetails"]["duration"])
        if v["status"].get("embeddable") and 10 <= d <= MAX_SEC and v["id"] not in seen:
            seen.add(v["id"]); items.append({"id": v["id"], "d": d})
if items:
    json.dump({"updated": datetime.datetime.utcnow().isoformat(),
               "videos": [i["id"] for i in items], "items": items},
              open("assets/videos.json", "w"))
print(len(items), "videos")
