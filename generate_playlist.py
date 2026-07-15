import requests
import re
import time
import os
import concurrent.futures
from datetime import datetime

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

# Keep only Tamil + English
MASTER_MAP = {
    # Tamil
    "sun tv": "Tamil - General Entertainment (GEC)", "star vijay": "Tamil - General Entertainment (GEC)",
    "zee tamil": "Tamil - General Entertainment (GEC)", "colors tamil": "Tamil - General Entertainment (GEC)",
    "kalaignar tv": "Tamil - General Entertainment (GEC)", "jaya tv": "Tamil - General Entertainment (GEC)",
    "raj tv": "Tamil - General Entertainment (GEC)", "polimer tv": "Tamil - General Entertainment (GEC)",
    "dd tamil": "Tamil - General Entertainment (GEC)",
    "ktv": "Tamil - Movies", "vijay super": "Tamil - Movies", "zee thirai": "Tamil - Movies",
    "raj digital plus": "Tamil - Movies", "sun action": "Tamil - Movies",
    "sun news": "Tamil - News", "thanthi tv": "Tamil - News", "polimer news": "Tamil - News",
    "news7 tamil": "Tamil - News", "puthiya thalaimurai": "Tamil - News",
    "sun music": "Tamil - Music", "vijay music": "Tamil - Music",
    "chutti tv": "Tamil - Kids", "discovery tamil": "Tamil - Infotainment & Lifestyle",
    "madha tv": "Tamil - Spiritual & Devotional",
    # English
    "star movies": "English - Movies", "sony pix": "English - Movies", "movies now": "English - Movies",
    "times now": "English - News", "republic tv": "English - News", "cnn news18": "English - News",
    "bbc news": "English - News", "cnn international": "English - News", "al jazeera english": "English - News",
    "star sports 1": "English - Sports", "sony sports ten 1": "English - Sports",
    "cartoon network": "English - Kids", "nickelodeon": "English - Kids", "disney channel": "English - Kids",
    "discovery channel": "English - Infotainment", "national geographic": "English - Infotainment",
    "zee cafe": "English - General Entertainment (GEC)", "colors infinity": "English - General Entertainment (GEC)",
}

HEADERS = {"User-Agent": "VLC/3.0.20 LibVLC/3.0.20"}
BLOCK_WORDS = ("telugu", "kannada", "malayalam", "hindi", "marathi", "bengali", "punjabi", "gujarati", "urdu", "bhojpuri")

def clean_name(raw):
    raw = re.sub(r'\s*\[.*?\]\s*', '', raw)
    raw = re.sub(r'\s*\(.*?\)\s*', '', raw)
    raw = re.sub(r'\s*\b(HD|SD|FHD|HEVC|4K|UHD|1080p|720p)\b\s*', '', raw, flags=re.I)
    return ' '.join(raw.split()).strip()

def get_category(name_str, is_local):
    clean = clean_name(name_str).lower()
    if any(w in clean for w in BLOCK_WORDS):
        return None
    if clean in MASTER_MAP:
        return MASTER_MAP[clean]
    for k, v in MASTER_MAP.items():
        if re.search(r'\b' + re.escape(k) + r'\b', clean):
            return v
    return "Tamil - Local" if is_local else None

def fetch_channels(url, is_local):
    channels = []
    print(f"Fetching {url}...", flush=True)
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        name, cat, attrs = None, None, {}
        for line in r.text.splitlines():
            line = line.strip()
            if line.startswith("#EXTINF"):
                name_str = line.rsplit(',', 1)[-1].strip()
                cat = get_category(name_str, is_local)
                if cat:
                    name = name_str
                    attrs = dict(re.findall(r'(\S+)="(.*?)"', line))
                else:
                    name = None
            elif line.startswith("http") and name:
                channels.append((line, cat, attrs, name, clean_name(name).lower()))
                name = None
        print(f" Found {len(channels)} candidates")
    except Exception as e:
        print(f" FAIL: {e}")
    return channels

def test_link(ch):
    url, cat, attrs, name, norm = ch
    try:
        start = time.time()
        r = requests.get(url, headers=HEADERS, timeout=12, stream=True, allow_redirects=True)
        dt = time.time() - start
        if r.status_code == 200 and dt < 8:
            chunk = r.raw.read(1024)
            if b'#EXTM3U' in chunk or b'.ts' in chunk or b'.m3u8' in chunk:
                r.close()
                return ch + (dt,)
        r.close()
    except:
        pass
    return None

def main():
    old_playlist = None
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            old_playlist = f.read()

    raw_channels = []
    for s in SOURCES_GENERAL:
        raw_channels.extend(fetch_channels(s, False))
    for s in SOURCES_LOCAL:
        raw_channels.extend(fetch_channels(s, True))

    # group by name to dedupe
    by_name = {}
    for ch in raw_channels:
        by_name.setdefault(ch[4], []).append(ch)

    print(f"\nTesting {len(by_name)} unique channels for working streams...\n")

    valid_channels = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for name, group in by_name.items():
            results = list(executor.map(test_link, group))
            working = [r for r in results if r]
            if working:
                best = min(working, key=lambda x: x[5]) # fastest
                valid_channels.append(best[:5])

    output = {cat: [] for cat in CATEGORIES}
    seen_urls = set()
    for url, cat, attrs, ch_name, norm in valid_channels:
        if url in seen_urls:
            continue
        seen_urls.add(url)
        attrs["group-title"] = cat
        output[cat].append((ch_name, url, attrs))

    for cat in output:
        output[cat].sort(key=lambda x: x[0].lower())

    total = sum(len(v) for v in output.values())

    if total == 0 and old_playlist:
        print("No channels found. Restoring backup.")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(old_playlist)
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cat in CATEGORIES:
            if output[cat]:
                f.write(f"\n# --- {cat} ---\n")
                for ch_name, url, attrs in output[cat]:
                    attr_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])
                    f.write(f'#EXTINF:-1 {attr_str},{ch_name}\n')
                    f.write(f'{url}\n')

    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        f.write(open(OUTPUT_FILE, encoding="utf-8").read())

    # README
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("# 📺 Tamil & English IPTV\n")
        f.write(f"**Last Updated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
        f.write(f"**Live Working Channels:** {total}\n\n")
        f.write("| Category | Channels |\n| --- | --- |\n")
        for cat in CATEGORIES:
            if output[cat]:
                f.write(f"| {cat} | {len(output[cat])} |\n")

    print(f"\n✅ DONE: {total} LIVE Tamil + English channels")
    for cat in CATEGORIES:
        if output[cat]:
            print(f" {cat}: {len(output[cat])}")

if __name__ == "__main__":
    main()
