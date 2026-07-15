import requests
import re
import time
import os
import concurrent.futures

OUTPUT_FILE = "playlist.m3u"
BACKUP_FILE = "playlist_backup.m3u"

SOURCES_GENERAL = [
    "https://raw.githubusercontent.com/Vmfm/tamilvmtv/main/live/jio.m3u",
    "https://raw.githubusercontent.com/Tamilwebcast/Tamilwebcast.github.io/main/TWCIPTV.m3u",
    "https://raw.githubusercontent.com/Indiblog/india-iptv/main/output/india_iptv.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/jtv.m3u",
    "https://iptv-org.github.io/iptv/languages/tam.m3u",
    "https://iptv-org.github.io/iptv/languages/eng.m3u"
]

SOURCES_LOCAL = [
    "https://raw.githubusercontent.com/Vmfm/tamilvmtv/main/live/channels.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/ashokadigital.m3u",
    "https://raw.githubusercontent.com/amazeyourself/tamil-local-iptv/refs/heads/main/channels.m3u"
]

CATEGORIES = [
    "Tamil - General Entertainment (GEC)", "Tamil - Movies", "Tamil - News",
    "Tamil - Comedy", "Tamil - Music", "Tamil - Infotainment & Lifestyle",
    "Tamil - Spiritual & Devotional", "Tamil - Kids", "Tamil - Local",
    "English - General Entertainment (GEC)", "English - Movies", "English - National News",
    "English - International News", "English - Business News", "English - Infotainment",
    "English - Lifestyle & Travel", "English - Kids", "English - Sports"
]

MASTER_MAP = {... } # Keep your same MASTER_MAP from before

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
BLOCK_WORDS = ("telugu", "kannada", "malayalam", "hindi", "marathi", "bengali", "punjabi", "gujarati", "urdu", "bhojpuri", "odiya", "assamese")

def clean_name(raw):
    raw = re.sub(r'\s*\[.*?\]\s*', '', raw)
    raw = re.sub(r'\s*\(.*?\)\s*', '', raw)
    raw = re.sub(r'\s*\b(HD|SD|FHD|HEVC|4K|UHD|HDR|Dolby|1080p|720p|Premium|IN)\b\s*', '', raw, flags=re.I)
    return ' '.join(raw.split()).strip()

def get_category(name_str, is_local_source):
    clean = clean_name(name_str).lower()
    if any(w in clean for w in BLOCK_WORDS):
        return None
    if clean in MASTER_MAP:
        return MASTER_MAP[clean]
    for k, v in MASTER_MAP.items():
        if re.search(r'\b' + re.escape(k) + r'\b', clean):
            return v
    if is_local_source:
        return "Tamil - Local"
    return None

def fetch_channels(url, is_local_source=False):
    channels = []
    print(f"Fetching {url}... ", end="", flush=True)
    try:
        with requests.get(url, headers=HEADERS, timeout=15) as resp:
            resp.raise_for_status()
            attrs, name, current_cat = {}, None, None
            for line in resp.text.splitlines():
                line = line.strip()
                if line.startswith("#EXTINF"):
                    name_str = line.rsplit(',', 1)[-1].strip()
                    category = get_category(name_str, is_local_source)
                    if category:
                        name, current_cat = name_str, category
                        attrs = dict(re.findall(r'(\S+)="(.*?)"', line))
                    else:
                        name = None
                elif line.startswith("http") and name:
                    channels.append((line, current_cat, attrs, name, clean_name(name).lower()))
                    name = None
        print(f"OK ({len(channels)})")
    except Exception as e:
        print(f"FAIL ({e})")
    return channels

def test_link(channel_data):
    """Test with 2 retries, 10s timeout. Must return 200 and >100 bytes"""
    url = channel_data[0]
    for i in range(2):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10, stream=True, allow_redirects=True)
            if r.status_code == 200:
                content = next(r.iter_content(1024), b'')
                r.close()
                if len(content) > 100: # dead links often return 0 bytes
                    return channel_data + (r.elapsed.total_seconds(),) # add speed
            r.close()
        except:
            pass
        time.sleep(1)
    return None

def main():
    old_playlist = open(OUTPUT_FILE, encoding="utf-8").read() if os.path.exists(OUTPUT_FILE) else None

    raw_channels = []
    for s in SOURCES_GENERAL: raw_channels.extend(fetch_channels(s, False))
    for s in SOURCES_LOCAL: raw_channels.extend(fetch_channels(s, True))

    # Dedupe by name, keep all URLs to test
    channels_by_name = {}
    for ch in raw_channels:
        channels_by_name.setdefault(ch[4], []).append(ch)

    print(f"\nTesting {len(channels_by_name)} unique channels with 10s timeout...\n")

    valid_channels = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        for name, group in channels_by_name.items():
            # test all URLs for this channel, take fastest working one
            results = list(executor.map(test_link, group))
            working = [r for r in results if r]
            if working:
                best = min(working, key=lambda x: x[5]) # fastest
                valid_channels.append(best[:5]) # drop speed

    output = {cat: [] for cat in CATEGORIES}
    seen_urls = set()
    for url, cat, attrs, ch_name, norm in valid_channels:
        if url in seen_urls: continue # global dedupe
        seen_urls.add(url)
        attrs["group-title"] = cat
        output[cat].append((ch_name, url, attrs))

    for cat in output: output[cat].sort(key=lambda x: x[0].lower())
    total = sum(len(v) for v in output.values())

    if total == 0 and old_playlist:
        print("No channels found. Restoring backup.")
        open(OUTPUT_FILE, "w", encoding="utf-8").write(old_playlist)
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cat in CATEGORIES:
            if output[cat]:
                f.write(f"\n# --- {cat} ---\n")
                for ch_name, url, attrs in output[cat]:
                    extinf = '#EXTINF:-1 ' + ' '.join([f'{k}="{v}"' for k,v in attrs.items()]) + f',{ch_name}'
                    f.write(extinf + '\n' + url + '\n')

    open(BACKUP_FILE, "w", encoding="utf-8").write(open(OUTPUT_FILE).read())
    print(f"\n✅ {total} LIVE Tamil + English channels")
    for cat in CATEGORIES:
        if output[cat]: print(f" {cat}: {len(output[cat])}")

if __name__ == "__main__": main()
