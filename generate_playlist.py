import requests, re, time, os
from collections import OrderedDict

OUTPUT_FILE = "playlist.m3u"
BACKUP_FILE = "playlist_backup.m3u"

# iptv-org language-specific playlists – already tested and live
TAMIL_URL = "https://iptv-org.github.io/iptv/languages/tam.m3u"
ENGLISH_URL = "https://iptv-org.github.io/iptv/languages/eng.m3u"

CATEGORIES = [
    "Tamil Entertainment", "Tamil News", "Tamil Movies", "Tamil Music",
    "Tamil Kids", "Tamil Sports", "Tamil Devotional", "Tamil Infotainment",
    "Tamil Shopping", "Tamil Local", "English Movies", "English News"
]

# Master list for categorization (if group-title is missing)
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
    "hbo": "English Movies", "star movies": "English Movies",
    "sony pix": "English Movies", "mn+": "English Movies",
    "&flix": "English Movies", "romedy now": "English Movies",
    "comedy central": "English Movies"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def clean_name(raw):
    raw = re.sub(r'\s*\[.*?\]\s*', '', raw)
    raw = re.sub(r'\s*\(.*?\)\s*', '', raw)
    raw = re.sub(r'\s*\b(HD|SD|HEVC|4K|UHD|HDR|Dolby)\b\s*', '', raw, flags=re.I)
    return ' '.join(raw.split()).strip()

def get_category(name, group_title=""):
    """Categorize using group-title first, then master list."""
    # If source already provides a meaningful group-title, use it directly
    valid_cats = {cat.lower(): cat for cat in CATEGORIES}
    if group_title and group_title.lower() in valid_cats:
        return valid_cats[group_title.lower()]

    clean = clean_name(name).lower()
    for master_name, category in MASTER_LIST.items():
        if master_name in clean or clean in master_name:
            return category

    # Fallback for Tamil-sounding channels
    tamil_kw = ["tamil", "sun ", "vijay", "kalaignar", "jaya ", "raj ",
                "polimer", "mega ", "vasanth", "vendhar", "captain",
                "adithya", "puthu", "makkal", "sirippoli", "isai",
                "seithigal", "thanthi", "chutti", "thirai", "musix",
                "aruvi", "sathiyam", "murugan", "angel", "dd podhigai"]
    if any(kw in clean for kw in tamil_kw):
        return "Tamil Local"

    # Fallback for English channels
    eng_kw = ["cnn", "bbc", "hbo", "star movies", "disney", "discovery",
              "nat geo", "fox", "sony pix", "mn+", "bloomberg", "news"]
    if any(kw in clean for kw in eng_kw):
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

def fetch_channels(url, default_lang):
    """Return list of (category, attrs, raw_name, url) from an M3U URL."""
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
        group = attrs.get("group-title", "")
        cat = get_category(raw_name, group)
        if cat is None:
            # Use default language category if nothing else matched
            if default_lang == "tamil":
                cat = "Tamil Local"
            else:
                cat = "English Movies"
        channels.append((cat, attrs, raw_name, stream_url))
    return channels

def main():
    # Backup old playlist
    old_playlist = None
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            old_playlist = f.read()

    # Fetch Tamil and English playlists
    tamil_channels = fetch_channels(TAMIL_URL, "tamil")
    english_channels = fetch_channels(ENGLISH_URL, "english")

    # Merge, deduplicate by URL
    output = {cat: OrderedDict() for cat in CATEGORIES}
    seen_urls = set()
    for cat, attrs, raw_name, url in tamil_channels + english_channels:
        if url in seen_urls:
            continue
        seen_urls.add(url)
        new_attrs = dict(attrs)
        new_attrs["group-title"] = cat
        output[cat][url] = (new_attrs, raw_name)

    total = sum(len(v) for v in output.values())
    if total == 0:
        print("⚠️ No channels fetched. Restoring previous playlist.")
        if old_playlist:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(old_playlist)
        else:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n# No channels available\n")
        return

    # Write final playlist
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

    # Backup
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        f.write(open(OUTPUT_FILE).read())

    print(f"\n✅ Playlist created: {total} live channels")
    for cat in CATEGORIES:
        if output[cat]:
            print(f"  {cat}: {len(output[cat])}")

    # Update README
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("# 📺 Tamil & English IPTV (iptv-org sources)\n\n")
        f.write(f"**Updated:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n\n")
        f.write(f"**Live channels:** {total}\n\n")
        f.write("| Category | Channels |\n| --- | --- |\n")
        for cat in CATEGORIES:
            f.write(f"| {cat} | {len(output[cat])} |\n")
        f.write("\n## Usage\n`https://raw.githubusercontent.com/nuttle-nuttterr/Mk-test-ds/main/playlist.m3u`\n")

if __name__ == "__main__":
    main()
