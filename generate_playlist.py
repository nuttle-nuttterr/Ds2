import requests
import re
import time
import os
from collections import OrderedDict

OUTPUT_FILE = "playlist.m3u"
BACKUP_FILE = "playlist_backup.m3u"

TAMIL_URL = "https://iptv-org.github.io/iptv/languages/tam.m3u"
ENGLISH_URL = "https://iptv-org.github.io/iptv/languages/eng.m3u"

CATEGORIES = [
    "Tamil Entertainment", "Tamil News", "Tamil Movies", "Tamil Music",
    "Tamil Kids", "Tamil Sports", "Tamil Devotional", "Tamil Infotainment",
    "Tamil Shopping", "Tamil Local", "English Movies", "English News"
]

TAMIL_KW = [
    "tamil", "sun ", "vijay", "kalaignar", "jaya ", "raj ", "captain",
    "polimer", "mega ", "pudhiya", "thanthi", "vasanth", "isaiaruvi",
    "k tv", "ktv", "adithya", "chutti", "chithiram", "makkal", "sirippoli",
    "vendhar", "peppers", "angel", "murugan", "madha", "velicham", "seithigal",
    "podhigai", "puthiya", "thalaimurai", "sathiyam", "madhimugam",
    "aruloli", "jeevan", "nambikkai", "shubhsandesh", "aastha"
]

ENGLISH_KW = [
    "english", "hbo", "cnn", "bbc", "disney", "discovery", "nat geo",
    "sony pix", "star movies", "mn+", "hits", "romedy", "comedy central",
    "axn", "colors infinity", "zee café", "&flix", "&privé", "star world",
    "fox", "fyi", "tlc", "animal planet", "history tv18", "bloomberg",
    "movies now", "sky news", "ndtv", "wion", "times now"
]

BLOCKED = [
    "telugu", "hindi", "marathi", "malayalam", "kannada", "bengali", "punjabi",
    "gujarati", "oriya", "assamese", "bhojpuri", "urdu", "sanskrit",
    "etv", "gemini", "maa tv", "tv9", "zee marathi", "star pravah",
    "asianet", "kiran", "flowers", "mazhavil", "kairali", "amrita",
    "sangeet", "b4u", "aaj tak", "sony sab", "sony pal",
    "star plus", "zee tv", "star utsav", "star gold", "sony max",
    "dangal", "big magic", "dd national", "dd india", "sony max 2",
    "colors kannada", "colors bangla", "colors gujarati", "colors marathi"
]

MASTER_LIST = {
    "sun tv": "Tamil Entertainment", "star vijay": "Tamil Entertainment",
    "zee tamil": "Tamil Entertainment", "colors tamil": "Tamil Entertainment",
    "kalaignar tv": "Tamil Entertainment", "raj tv": "Tamil Entertainment",
    "polimer tv": "Tamil Entertainment", "mega tv": "Tamil Entertainment",
    "vasanth tv": "Tamil Entertainment", "puthuyugam tv": "Tamil Entertainment",
    "captain tv": "Tamil Entertainment", "adithya tv": "Tamil Entertainment",
    "vendhar tv": "Tamil Entertainment", "jaya tv": "Tamil Entertainment",
    "d tamil": "Tamil Entertainment", "sirippoli": "Tamil Entertainment",
    "sun news": "Tamil News", "raj news": "Tamil News",
    "thanthi tv": "Tamil News", "news18 tamil": "Tamil News",
    "polimer news": "Tamil News", "news7 tamil": "Tamil News",
    "news j": "Tamil News", "kalaignar seithigal": "Tamil News",
    "win news": "Tamil News", "sathiyam tv": "Tamil News",
    "madhimugam tv": "Tamil News", "pudhiya thalaimurai": "Tamil News",
    "ktv": "Tamil Movies", "zee thirai": "Tamil Movies",
    "sun life": "Tamil Movies", "raj digital plus": "Tamil Movies",
    "jaya movie": "Tamil Movies", "vijay super": "Tamil Movies",
    "j movies": "Tamil Movies", "thirai tv": "Tamil Movies",
    "sun music": "Tamil Music", "raj musix": "Tamil Music",
    "isaiaruvi": "Tamil Music", "g music": "Tamil Music",
    "jcv musix": "Tamil Music", "chutti tv": "Tamil Kids",
    "chithiram tv": "Tamil Kids", "cartoon network tamil": "Tamil Kids",
    "pogo tamil": "Tamil Kids", "nick tamil": "Tamil Kids",
    "sony yay tamil": "Tamil Kids", "star sports tamil": "Tamil Sports",
    "angel tv": "Tamil Devotional", "murugan tv": "Tamil Devotional",
    "discovery tamil": "Tamil Infotainment", "sony bbc earth": "Tamil Infotainment",
    "cnn": "English News", "bbc news": "English News",
    "bloomberg": "English News", "ndtv 24x7": "English News",
    "wion": "English News", "times now": "English News",
    "sky news": "English News",
    "hbo": "English Movies", "star movies": "English Movies",
    "sony pix": "English Movies", "mn+": "English Movies",
    "&flix": "English Movies", "romedy now": "English Movies",
    "comedy central": "English Movies"
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean_name(raw):
    raw = re.sub(r'\s*\[.*?\]\s*', '', raw)
    raw = re.sub(r'\s*\(.*?\)\s*', '', raw)
    raw = re.sub(r'\s*\b(HD|SD|HEVC|4K|UHD|HDR|Dolby)\b\s*', '', raw, flags=re.I)
    return ' '.join(raw.split()).strip()

def detect_language(name):
    n = name.lower()
    for word in BLOCKED:
        if word in n:
            return None
    for kw in TAMIL_KW:
        if kw in n:
            return "tamil"
    for kw in ENGLISH_KW:
        if kw in n:
            return "english"
    return None

def get_category(name, group_title=""):
    clean = clean_name(name).lower()
    for master_name, category in MASTER_LIST.items():
        if master_name in clean or clean in master_name:
            return category
    if any(kw in clean for kw in TAMIL_KW):
        return "Tamil Local"
    if any(kw in clean for kw in ENGLISH_KW):
        return "English News" if "news" in clean else "English Movies"
    return None

def parse_m3u(content):
    lines = content.splitlines()
    attrs = {}
    name = None
    for line in lines:
        line = line.strip()
        if line.startswith("#EXTINF"):
            attrs = {}
            for match in re.finditer(r'(\S+)="(.*?)"', line):
                attrs[match.group(1)] = match.group(2)
            if ',' in line:
                name = line.rsplit(',', 1)[-1].strip()
            else:
                name = None
        elif line and not line.startswith("#") and name:
            yield attrs, name, line
            name = None

def validate_stream(url, timeout=5):
    """
    Check if the stream URL is reachable and returns a success status.
    Returns (True, response_time) or (False, None).
    """
    try:
        start = time.time()
        # Use a GET request with stream=True to only read headers and first few bytes
        resp = requests.get(url, headers=HEADERS, timeout=timeout, stream=True)
        # Check if status is 2xx or 3xx (redirects are okay)
        if 200 <= resp.status_code < 400:
            # Read a small chunk to ensure data is actually coming
            chunk = resp.raw.read(1024)
            resp.close()
            elapsed = time.time() - start
            return True, elapsed
        else:
            resp.close()
            return False, None
    except Exception:
        return False, None

def fetch_channels(url, default_lang):
    channels = []
    print(f"Fetching {url} ... ", end="")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        print("OK")
    except Exception as e:
        print(f"FAIL ({e})")
        return channels

    for attrs, raw_name, stream_url in parse_m3u(resp.text):
        stream_url = stream_url.strip()
        if not stream_url.startswith("http"):
            continue

        lang = detect_language(raw_name)
        if lang is None:
            continue

        cat = get_category(raw_name, attrs.get("group-title", ""))
        if cat is None:
            cat = "Tamil Local" if lang == "tamil" else "English Movies"

        # ---------- VALIDATE THE STREAM ----------
        print(f"  Testing: {raw_name[:40]}... ", end="")
        ok, elapsed = validate_stream(stream_url)
        if ok:
            print(f"✓ ({elapsed:.2f}s)")
            channels.append((cat, attrs, raw_name, stream_url))
        else:
            print("✗ (dead/slow)")

    return channels

def main():
    old_playlist = None
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            old_playlist = f.read()

    tamil = fetch_channels(TAMIL_URL, "tamil")
    english = fetch_channels(ENGLISH_URL, "english")

    output = {cat: OrderedDict() for cat in CATEGORIES}
    seen = set()
    for cat, attrs, raw_name, url in tamil + english:
        if url in seen:
            continue
        seen.add(url)
        new_attrs = dict(attrs)
        new_attrs["group-title"] = cat
        output[cat][url] = (new_attrs, raw_name)

    total = sum(len(v) for v in output.values())
    if total == 0:
        print("⚠️ No valid channels found. Restoring previous playlist.")
        if old_playlist:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(old_playlist)
        else:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n# No working channels\n")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cat in CATEGORIES:
            if not output[cat]:
                continue
            f.write(f"\n# --- {cat} ---\n")
            for url, (attrs, ch_name) in output[cat].items():
                extinf = '#EXTINF:-1'
                for k, v in attrs.items():
                    extinf += f' {k}="{v}"'
                extinf += f',{ch_name}'
                f.write(extinf + '\n')
                f.write(url + '\n')

    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        f.write(open(OUTPUT_FILE).read())

    print(f"\n✅ Playlist created: {total} live channels")
    for cat in CATEGORIES:
        if output[cat]:
            print(f"  {cat}: {len(output[cat])}")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("# 📺 Tamil & English IPTV\n\n")
        f.write(f"**Updated:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n\n")
        f.write(f"**Live channels:** {total}\n\n")
        f.write("| Category | Channels |\n| --- | --- |\n")
        for cat in CATEGORIES:
            f.write(f"| {cat} | {len(output[cat])} |\n")
        f.write("\n## Usage\n`https://raw.githubusercontent.com/nuttle-nuttterr/Mk-test-ds/main/playlist.m3u`\n")

if __name__ == "__main__":
    main()
