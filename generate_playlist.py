import requests
import re
import time
import os
import concurrent.futures

OUTPUT_FILE = "playlist.m3u"
BACKUP_FILE = "playlist_backup.m3u"

SOURCES_GENERAL = [
    "https://iptv-org.github.io/iptv/languages/tam.m3u",
    "https://iptv-org.github.io/iptv/languages/eng.m3u",
    "https://raw.githubusercontent.com/Vmfm/tamilvmtv/main/live/jio.m3u",
    "https://raw.githubusercontent.com/Tamilwebcast/Tamilwebcast.github.io/main/TWCIPTV.m3u",
]
SOURCES_LOCAL = [
    "https://raw.githubusercontent.com/Vmfm/tamilvmtv/main/live/channels.m3u",
    "https://raw.githubusercontent.com/amazeyourself/tamil-local-iptv/refs/heads/main/channels.m3u"
]

CATEGORIES = [
    "Tamil - General Entertainment (GEC)", "Tamil - Movies", "Tamil - News",
    "Tamil - Music", "Tamil - Local", "Tamil - Spiritual & Devotional", "Tamil - Kids",
    "English - General Entertainment (GEC)", "English - Movies", "English - News",
    "English - Sports", "English - Kids", "English - Infotainment"
]
# Shortened MASTER_MAP for brevity - keep your full one
MASTER_MAP = { "sun tv": "Tamil - General Entertainment (GEC)", "star vijay": "Tamil - General Entertainment (GEC)", "zee tamil": "Tamil - General Entertainment (GEC)", "colors tamil": "Tamil - General Entertainment (GEC)", "ktv": "Tamil - Movies", "sun news": "Tamil - News", "thanthi tv": "Tamil - News", "sun music": "Tamil - Music", "chutti tv": "Tamil - Kids", "star movies": "English - Movies", "sony pix": "English - Movies", "times now": "English - News", "bbc news": "English - News", "cnn international": "English - News", "star sports 1": "English - Sports", "cartoon network": "English - Kids", "discovery channel": "English - Infotainment" } # ADD YOUR FULL MAP HERE

HEADERS = {"User-Agent": "VLC/3.0.20 LibVLC/3.0.20"}
BLOCK_WORDS = ("telugu", "kannada", "malayalam", "hindi", "marathi", "bengali", "punjabi", "gujarati", "urdu")

def clean_name(raw):
    raw = re.sub(r'\s*\[.*?\]\s*|\s*\(.*?\)\s*', '', raw)
    raw = re.sub(r'\s*\b(HD|SD|FHD|4K|1080p|720p)\b\s*', '', raw, flags=re.I)
    return ' '.join(raw.split()).strip()

def get_category(name_str, is_local):
    clean = clean_name(name_str).lower()
    if any(w in clean for w in BLOCK_WORDS): return None
    if clean in MASTER_MAP: return MASTER_MAP[clean]
    for k,v in MASTER_MAP.items():
        if re.search(r'\b' + re.escape(k) + r'\b', clean): return v
    return "Tamil - Local" if is_local else None

def fetch_channels(url, is_local):
    channels = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        lines = r.text.splitlines()
        name, cat, attrs = None, None, {}
        for line in lines:
            if line.startswith("#EXTINF"):
                name_str = line.rsplit(',', 1)[-1].strip()
                cat = get_category(name_str, is_local)
                if cat:
                    name, attrs = name_str, dict(re.findall(r'(\S+)="(.*?)"', line))
                else: name = None
            elif line.startswith("http") and name:
                channels.append((line, cat, attrs, name, clean_name(name).lower()))
                name = None
    except: pass
    return channels

def test_link(ch):
    url, cat, attrs, name, norm = ch
    try:
        start = time.time()
        r = requests.get(url, headers=HEADERS, timeout=15, stream=True)
        dt = time.time() - start
        if r.status_code == 200 and dt < 8: # Drop slow >8s links
            content = r.raw.read(512)
            if b'#EXTM3U' in content or b'.ts' in content or b'.m3u8' in content:
                r.close()
                return ch + (dt,)
        r.close()
    except: pass
    return None

def main():
    raw = []
    for s in SOURCES_GENERAL: raw.extend(fetch_channels(s, False))
    for s in SOURCES_LOCAL: raw.extend(fetch_channels(s, True))

    by_name = {}
    for ch in raw: by_name.setdefault(ch[4], []).append(ch)

    print(f"Testing {len(by_name)} unique channels...")
    valid = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex: # Lower workers = less timeouts
        for res in ex.map(lambda g: min([r for r in map(test_link, g) if r], key=lambda x: x[5], default=None), by_name.values()):
            if res: valid.append(res[:5])

    output = {c: [] for c in CATEGORIES}
    for url, cat, attrs, name, norm in valid:
        attrs["group-title"] = cat
        output[cat].append((name, url, attrs))

    for c in output: output[c].sort(key=lambda x: x[0].lower())
    total = sum(len(v) for v in output.values())

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for c in CATEGORIES:
            if output[c]:
                f.write(f"\n# --- {c} ---\n")
                for name, url, attrs in output[c]:
                    f.write(f'#EXTINF:-1 {" ".join([f"{k}=\"{v}\"" for k,v in attrs.items()])},{name}\n{url}\n')

    print(f"\n✅ FINAL: {total} WORKING channels")
    for c in CATEGORIES:
        if output[c]: print(f" {c}: {len(output[c])}")

if __name__ == "__main__": main()
