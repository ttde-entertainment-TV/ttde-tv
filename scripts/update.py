import json, os, re, glob, math, subprocess, urllib.request, urllib.parse, datetime
KEY = os.environ["YOUTUBE_API_KEY"]
API = "https://www.googleapis.com/youtube/v3/"
QUERIES = ["musica", "humor", "deportes", "viajes", "animales", "cocina", "tecnologia"]
MIN_S, MAX_S = 10, 240

def get(path, **p):
    p["key"] = KEY
    return json.load(urllib.request.urlopen(API + path + "?" + urllib.parse.urlencode(p)))

def dur(s):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s)
    h, mi, se = [int(x or 0) for x in m.groups()]
    return h * 3600 + mi * 60 + se

def details(ids):
    out = {}
    for i in range(0, len(ids), 50):
        d = get("videos", part="contentDetails,status", id=",".join(ids[i:i+50]))
        for v in d.get("items", []):
            out[v["id"]] = (dur(v["contentDetails"]["duration"]), v["status"].get("embeddable", False))
    return out

# 1) Mis videos de YouTube (mis_videos.txt)
own_yt = []
if os.path.exists("mis_videos.txt"):
    ids = []
    for line in open("mis_videos.txt", encoding="utf-8"):
        line = line.split("#")[0].strip()
        if not line: continue
        m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([\w-]{11})", line) or re.fullmatch(r"([\w-]{11})", line)
        if m and m.group(1) not in ids: ids.append(m.group(1))
    if ids:
        det = details(ids)
        own_yt = [{"id": i, "d": det[i][0]} for i in ids if i in det and det[i][1] and det[i][0] > 0]

# 2) Mis videos subidos (docs/videos/*.mp4)
own_files = []
for f in sorted(glob.glob("docs/videos/*.mp4") + glob.glob("docs/videos/*.webm")):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip()
        d = math.ceil(float(out))
        if d > 0: own_files.append({"src": "videos/" + urllib.parse.quote(os.path.basename(f)), "d": d})
    except Exception as e:
        print("no pude leer", f, e)
own = []
for a, b in zip(own_yt, own_files): own += [a, b]
own += own_yt[len(own_files):] + own_files[len(own_yt):]

# 3) Automaticos: YouTube con licencia Creative Commons
auto, seen = [], set(i.get("id") for i in own)
since = (datetime.datetime.utcnow() - datetime.timedelta(days=365)).strftime("%Y-%m-%dT00:00:00Z")
for q in QUERIES:
    try:
        r = get("search", part="id", type="video", videoLicense="creativeCommon",
                videoEmbeddable="true", videoDuration="short", order="viewCount",
                q=q, maxResults=50, relevanceLanguage="es", publishedAfter=since)
        ids = [x["id"]["videoId"] for x in r.get("items", []) if x["id"]["videoId"] not in seen]
        det = details(ids)
        for i in ids:
            if i in det and det[i][1] and MIN_S <= det[i][0] <= MAX_S:
                seen.add(i); auto.append({"id": i, "d": det[i][0]})
    except Exception as e:
        print("busqueda fallo", q, e)

# 4) Mezcla: 1 propio, luego 2 automaticos
items, ai = [], 0
for o in own:
    items.append(o)
    items += auto[ai:ai+2]; ai += 2
items += auto[ai:]
print(len(own), "propios,", len(auto), "automaticos")
if items:
    json.dump({"updated": datetime.datetime.utcnow().isoformat(),
               "videos": [i["id"] for i in items if "id" in i], "items": items},
              open("assets/videos.json", "w"))
