import json, os, re, glob, math, subprocess, urllib.request, urllib.parse, datetime
KEY = os.environ["YOUTUBE_API_KEY"]
API = "https://www.googleapis.com/youtube/v3/"
REGIONS = ["AR", "MX", "ES"]
MIN_S, MAX_S = 60, 10800          # de 1 min a 3 horas
OK_CATS = {"10", "19"}            # solo Musica y Viajes/Paisajes
LANGS = ("es", "en")
CHANNELS = [
    {"id": "estudiar", "name": "Estudiar", "q": "musica para estudiar", "kw": ["estudiar", "estudio", "concentracion", "study", "examen", "tarea"]},
    {"id": "trabajar", "name": "Trabajar", "q": "musica para trabajar concentrado", "kw": ["trabajar", "trabajo", "focus", "oficina", "productividad"]},
    {"id": "relax", "name": "Relax y paisajes", "q": "musica relajante paisajes", "kw": ["relax", "relajante", "relajacion", "paisajes", "calma", "meditacion", "spa"]},
    {"id": "lofi", "name": "Lofi", "q": "lofi hip hop relax", "kw": ["lofi", "lo-fi", "chill"]},
    {"id": "jazz", "name": "Jazz", "q": "jazz relajante cafe", "kw": ["jazz", "cafe", "bossa"]},
    {"id": "piano", "name": "Piano", "q": "piano relajante", "kw": ["piano", "instrumental", "clasica"]},
    {"id": "pop", "name": "Pop", "q": "pop en español videoclip oficial", "kw": ["pop", "artistas", "videoclip", "cantantes", "exitos"]},
    {"id": "reggaeton", "name": "Reggaeton", "q": "reggaeton exitos videoclip oficial", "kw": ["reggaeton", "urbano", "perreo", "trap", "bailar", "fiesta"]},
    {"id": "rock", "name": "Rock", "q": "rock en español exitos", "kw": ["rock", "guitarra", "banda"]},
    {"id": "latina", "name": "Musica latina", "q": "musica latina exitos", "kw": ["latina", "latino", "tango"]},
    {"id": "electronica", "name": "Electronica", "q": "musica electronica exitos", "kw": ["electronica", "electronic", "edm", "house", "techno", "dj", "dance", "remix"]},
    {"id": "cumbia", "name": "Cumbia", "q": "cumbia exitos", "kw": ["cumbia", "villera"]},
    {"id": "salsa", "name": "Salsa", "q": "salsa exitos", "kw": ["salsa"]},
    {"id": "bachata", "name": "Bachata", "q": "bachata exitos", "kw": ["bachata"]},
    {"id": "trap", "name": "Trap y Rap", "q": "trap latino exitos", "kw": ["trap", "rap", "hip hop", "hiphop", "freestyle"]},
    {"id": "clasica", "name": "Clasica", "q": "musica clasica relajante", "kw": ["clasica", "orquesta", "beethoven", "mozart"]},
    {"id": "ingles", "name": "Hits en ingles", "q": "pop hits english official video", "kw": ["ingles", "english", "hits", "billboard"]},
    {"id": "80s", "name": "Años 80", "q": "musica de los 80 exitos", "kw": ["80", "ochentas", "80s", "retro"]},
    {"id": "90s", "name": "Años 90", "q": "musica de los 90 exitos", "kw": ["90", "noventas", "90s"]},
    {"id": "baladas", "name": "Baladas", "q": "baladas romanticas", "kw": ["balada", "baladas", "romantica", "amor"]},
    {"id": "folklore", "name": "Folklore", "q": "folklore argentino exitos", "kw": ["folklore", "cuarteto", "zamba", "chacarera"]},
    {"id": "rocknac", "name": "Rock nacional", "q": "rock nacional argentino", "kw": ["rock nacional", "argentino", "argentina"]},
    {"id": "gym", "name": "Entrenar", "q": "musica para entrenar gym", "kw": ["gym", "entrenar", "ejercicio", "correr", "workout"]},
    {"id": "fiesta", "name": "Fiesta", "q": "musica para fiesta bailar", "kw": ["fiesta", "bailar", "party", "boliche"]},
    {"id": "dormir", "name": "Dormir", "q": "musica para dormir", "kw": ["dormir", "sueño", "noche", "descansar"]},
    {"id": "lluvia", "name": "Naturaleza", "q": "sonidos de lluvia naturaleza relajante", "kw": ["lluvia", "naturaleza", "sonidos", "bosque", "mar", "olas"]},
    {"id": "kpop", "name": "K-pop", "q": "kpop videoclip oficial", "kw": ["kpop", "k-pop", "coreano"]},
]
BAD = re.compile(r"maltrat|abus|gore|muert|asesin|accident|pelea|violen|tortur|crimen|sangre|"
                 r"suicid|porn|sexo|desnud|xxx|cruel|masacre|ataque|disparo|cadaver|tragedia|brutal", re.I)
NONLATIN = re.compile("[\u0370-\u1FFF\u3000-\uFFFF]")

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
        d = get("videos", part="contentDetails,status,snippet", id=",".join(ids[i:i+50]))
        for v in d.get("items", []):
            sn = v.get("snippet", {})
            out[v["id"]] = {
                "d": dur(v["contentDetails"]["duration"]),
                "emb": v["status"].get("embeddable", False),
                "lang": (sn.get("defaultAudioLanguage") or sn.get("defaultLanguage") or "").lower(),
                "title": sn.get("title", ""), "chan": sn.get("channelTitle", ""),
                "cat": sn.get("categoryId", ""),
            }
    return out

def ids_from(path):
    ids = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.split("#")[0].strip()
            if not line: continue
            m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([\w-]{11})", line) or re.fullmatch(r"([\w-]{11})", line)
            if m and m.group(1) not in ids: ids.append(m.group(1))
    return ids

blocked = set(ids_from("bloqueados.txt"))

# 1) Mis videos de YouTube
own_yt = []
ids = ids_from("mis_videos.txt")
if ids:
    det = details(ids)
    own_yt = [{"id": i, "d": det[i]["d"]} for i in ids if i in det and det[i]["emb"] and det[i]["d"] > 0]

# 2) Mis archivos de video
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

# 3) Automaticos: solo musica / paisajes, filtrados
def ok(t):
    if not (t["emb"] and MIN_S <= t["d"] <= MAX_S and t["cat"] in OK_CATS): return False
    if BAD.search(t["title"] + " " + t["chan"]): return False
    if t["lang"]: return t["lang"].startswith(LANGS)
    return not NONLATIN.search(t["title"])

seen = set(i.get("id") for i in own) | blocked
pools = []
for qi, ch in enumerate(CHANNELS):
    pool = []
    try:
        r = get("search", part="id", type="video", videoEmbeddable="true", safeSearch="strict",
                order="viewCount", q=ch["q"], maxResults=40, relevanceLanguage="es",
                regionCode=REGIONS[qi % 3])
        ids = [x["id"]["videoId"] for x in r.get("items", []) if x["id"]["videoId"] not in seen]
        det = details(ids)
        for i in ids:
            if i in det and ok(det[i]):
                seen.add(i); pool.append({"id": i, "d": det[i]["d"]})
    except Exception as e:
        print("busqueda fallo", ch["id"], e)
    pools.append(pool)
auto = []
for k in range(40):                       # intercala los temas
    for pool in pools:
        if k < len(pool): auto.append(pool[k])
auto = auto[:150]

# 4) Mezcla: 1 propio, luego 2 automaticos
items, ai = [], 0
for o in own:
    items.append(o)
    items += auto[ai:ai+2]; ai += 2
items += auto[ai:]
print(len(own), "propios,", len(auto), "automaticos")
if items:
    json.dump({"updated": datetime.datetime.utcnow().isoformat(),
               "videos": [i["id"] for i in items if "id" in i], "items": items,
               "channels": [{"id": c["id"], "name": c["name"], "kw": c["kw"], "items": p}
                            for c, p in zip(CHANNELS, pools) if p]},
              open("assets/videos.json", "w"))
