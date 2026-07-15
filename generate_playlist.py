import requests
import re
import time
import os
import concurrent.futures

OUTPUT_FILE = "playlist.m3u"
BACKUP_FILE = "playlist_backup.m3u"

# General sources
SOURCES_GENERAL = [
    "https://raw.githubusercontent.com/Vmfm/tamilvmtv/main/live/jio.m3u",
    "https://raw.githubusercontent.com/Tamilwebcast/Tamilwebcast.github.io/main/TWCIPTV.m3u",
    "https://raw.githubusercontent.com/Indiblog/india-iptv/main/output/india_iptv.m3u",
    "https://raw.githubusercontent.com/Indiblog/india-iptv/main/output/india_general.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/jtv.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/pishow.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/yupptvfast.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/tangotv.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/neotv.m3u",
    "https://iptv-org.github.io/iptv/languages/tam.m3u",
    "https://iptv-org.github.io/iptv/languages/eng.m3u"
]

# Tamil Local sources - also used to catch any Tamil channel not in MASTER_MAP
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

# Only Tamil + English channels allowed
MASTER_MAP = {
    # Tamil GEC
    "sun tv": "Tamil - General Entertainment (GEC)", "star vijay": "Tamil - General Entertainment (GEC)",
    "zee tamil": "Tamil - General Entertainment (GEC)", "colors tamil": "Tamil - General Entertainment (GEC)",
    "kalaignar tv": "Tamil - General Entertainment (GEC)", "jaya tv": "Tamil - General Entertainment (GEC)",
    "raj tv": "Tamil - General Entertainment (GEC)", "polimer tv": "Tamil - General Entertainment (GEC)",
    "makkal tv": "Tamil - General Entertainment (GEC)", "makkal": "Tamil - General Entertainment (GEC)",
    "vasanth tv": "Tamil - General Entertainment (GEC)", "puthuyugam tv": "Tamil - General Entertainment (GEC)",
    "mega tv": "Tamil - General Entertainment (GEC)", "captain tv": "Tamil - General Entertainment (GEC)",
    "vendhar tv": "Tamil - General Entertainment (GEC)", "dd tamil": "Tamil - General Entertainment (GEC)",

    # Tamil Movies
    "ktv": "Tamil - Movies", "star vijay super": "Tamil - Movies", "vijay super": "Tamil - Movies",
    "zee thirai": "Tamil - Movies", "j movie": "Tamil - Movies", "j movies": "Tamil - Movies",
    "raj digital plus": "Tamil - Movies", "murasu": "Tamil - Movies", "kalaignar murasu": "Tamil - Movies",
    "mega 24": "Tamil - Movies", "sun action": "Tamil - Movies", "thirai tv": "Tamil - Movies",

    # Tamil News
    "sun news": "Tamil - News", "puthiya thalaimurai": "Tamil - News", "puthiya": "Tamil - News",
    "thanthi tv": "Tamil - News", "news18 tamil nadu": "Tamil - News", "news18 tamil": "Tamil - News",
    "news18 tamil nadu nw18": "Tamil - News", "polimer news": "Tamil - News",
    "news7 tamil": "Tamil - News", "news7": "Tamil - News", "sathiyam tv": "Tamil - News",
    "news j": "Tamil - News", "jaya plus": "Tamil - News", "kalaignar seithigal": "Tamil - News",
    "raj news tamil": "Tamil - News", "captain news": "Tamil - News", "mathimugam": "Tamil - News",
    "malai murasu": "Tamil - News", "win news": "Tamil - News",

    # Tamil Comedy
    "adithya tv": "Tamil - Comedy", "sirippoli": "Tamil - Comedy", "siripoli": "Tamil - Comedy",

    # Tamil Music
    "sun music": "Tamil - Music", "star vijay music": "Tamil - Music", "vijay music": "Tamil - Music",
    "isaiaruvi": "Tamil - Music", "jaya max": "Tamil - Music", "raj musix tamil": "Tamil - Music",
    "mega musiq": "Tamil - Music", "jcv musix": "Tamil - Music",

    # Tamil Infotainment & Lifestyle
    "sun life": "Tamil - Infotainment & Lifestyle", "discovery tamil": "Tamil - Infotainment & Lifestyle",
    "nat geo tamil": "Tamil - Infotainment & Lifestyle", "sony bbc earth tamil": "Tamil - Infotainment & Lifestyle",

    # Tamil Spiritual & Devotional
    "madha tv": "Tamil - Spiritual & Devotional", "angel tv": "Tamil - Spiritual & Devotional",
    "nambikkai tv": "Tamil - Spiritual & Devotional", "vaanavil": "Tamil - Spiritual & Devotional",
    "jothi tv": "Tamil - Spiritual & Devotional", "velicham tv": "Tamil - Spiritual & Devotional",
    "sri sankara tv": "Tamil - Spiritual & Devotional", "sri sankara": "Tamil - Spiritual & Devotional",

    # Tamil Kids
    "chutti tv": "Tamil - Kids", "etv bal bharat tamil": "Tamil - Kids", "chithiram tv": "Tamil - Kids",

    # Tamil Local
    "sana tv": "Tamil - Local", "sana plus": "Tamil - Local", "utv": "Tamil - Local",
    "ntv": "Tamil - Local", "surya tv": "Tamil - Local", "subin tv": "Tamil - Local",
    "moon tv": "Tamil - Local", "sakthi tv": "Tamil - Local", "prime tv": "Tamil - Local",
    "d tv": "Tamil - Local", "tdn": "Tamil - Local", "7 green": "Tamil - Local",
    "yet tv": "Tamil - Local", "pr tv": "Tamil - Local", "riya tv": "Tamil - Local",
    "dark tv": "Tamil - Local", "harin tv": "Tamil - Local", "phoenix tv": "Tamil - Local",
    "roja tv": "Tamil - Local", "nila tv": "Tamil - Local", "smcv tv": "Tamil - Local",
    "aps tv": "Tamil - Local", "aps gold": "Tamil - Local", "mtv men": "Tamil - Local",
    "msn tv": "Tamil - Local", "veerali tv": "Tamil - Local", "three star tv": "Tamil - Local",
    "shalini tv": "Tamil - Local", "jcv tv": "Tamil - Local", "thendral tv": "Tamil - Local",
    "anbu tv": "Tamil - Local", "nellai tv": "Tamil - Local", "akash tv": "Tamil - Local",
    "apple tv": "Tamil - Local", "jeyson tv": "Tamil - Local", "jj max": "Tamil - Local",
    "jc tv": "Tamil - Local", "digital tv": "Tamil - Local", "oscar tv": "Tamil - Local",
    "jeyan tv": "Tamil - Local", "vidyal tv": "Tamil - Local", "kcn tv": "Tamil - Local",
    "sky tv": "Tamil - Local", "boys tv": "Tamil - Local", "king tv": "Tamil - Local",
    "udhayam tv": "Tamil - Local", "tn tv": "Tamil - Local", "senthamil tv": "Tamil - Local",
    "karur tv": "Tamil - Local", "karur city": "Tamil - Local", "bharathi tv": "Tamil - Local",
    "mcn tv": "Tamil - Local", "stn tv": "Tamil - Local", "suriyan tv": "Tamil - Local",
    "eesan tv": "Tamil - Local", "jeyam tv": "Tamil - Local", "solai tv": "Tamil - Local",
    "thalaa tv tam": "Tamil - Local",

    # English GEC
    "zee cafe": "English - General Entertainment (GEC)", "colors infinity": "English - General Entertainment (GEC)",
    "comedy central": "English - General Entertainment (GEC)", "disney international hd": "English - General Entertainment (GEC)",
    "disney international": "English - General Entertainment (GEC)",

    # English Movies
    "star movies": "English - Movies", "star movies select": "English - Movies", "sony pix": "English - Movies",
    "movies now": "English - Movies", "mnx": "English - Movies", "mn+": "English - Movies",
    "&flix": "English - Movies", "&prive hd": "English - Movies", "&prive": "English - Movies",
    "romedy now": "English - Movies",

    # English National News
    "times now": "English - National News", "republic tv": "English - National News",
    "cnn news18": "English - National News", "cnn-news18": "English - National News",
    "india today": "English - National News", "ndtv 24x7": "English - National News",
    "newsx": "English - National News", "mirror now": "English - National News", "wion": "English - National News",

    # English International News
    "bbc news": "English - International News", "cnn international": "English - International News",
    "al jazeera english": "English - International News", "rt": "English - International News",
    "russia today": "English - International News",

    # English Business News
    "cnbc tv18": "English - Business News", "cnbc-tv18": "English - Business News", "et now": "English - Business News",
    "ndtv profit": "English - Business News",

    # English Infotainment
    "discovery channel": "English - Infotainment", "national geographic": "English - Infotainment",
    "history tv18": "English - Infotainment", "animal planet": "English - Infotainment",
    "sony bbc earth": "English - Infotainment",

    # English Lifestyle & Travel
    "tlc": "English - Lifestyle & Travel", "travelxp": "English - Lifestyle & Travel", "goodtimes": "English - Lifestyle & Travel",

    # English Kids
    "cartoon network": "English - Kids", "nickelodeon": "English - Kids", "nick": "English - Kids",
    "pogo": "English - Kids", "disney channel": "English - Kids", "disney junior": "English - Kids",
    "sonic": "English - Kids", "super hungama": "English - Kids", "discovery kids": "English - Kids",
    "babytv": "English - Kids",

    # English Sports
    "star sports 1": "English - Sports", "star sports 2": "English - Sports",
    "star sports select 1": "English - Sports", "star sports select 2": "English - Sports",
    "sony sports ten 1": "English - Sports", "sony sports ten 2": "English - Sports",
    "sony sports ten 5": "English - Sports", "eurosport": "English - Sports",
    "sports18 1": "English - Sports", "sports18 - 1": "English - Sports"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

BLOCK_WORDS = ("telugu", "kannada", "malayalam", "hindi", "marathi", "bengali", "punjabi", "gujarati", "urdu", "bhojpuri", "odiya", "assamese")

def clean_name(raw):
    raw = re.sub(r'\s*\[.*?\]\s*', '', raw)
    raw = re.sub(r'\s*\(.*?\)\s*', '', raw)
    raw = re.sub(r'\s*\b(HD|SD|FHD|HEVC|4K|UHD|HDR|Dolby|1080p|720p|Premium|IN)\b\s*', '', raw, flags=re.I)
    return ' '.join(raw.split()).strip()

def contains_block_word(name):
    name_l = name.lower()
    return any(w in name_l for w in BLOCK_WORDS)

def get_category(name_str, is_local_source):
    clean = clean_name(name_str).lower()

    # Block other languages immediately
    if contains_block_word(clean):
        return None

    # 1. Exact match
    if clean in MASTER_MAP:
        return MASTER_MAP[clean]

    # 2. Boundary match
    for k, v in MASTER_MAP.items():
        if re.search(r'\b' + re.escape(k) + r'\b', clean):
            return v

    # 3. If from local tamil source and no block words, accept as Tamil Local
    if is_local_source:
        return "Tamil - Local"

    return None

def fetch_channels(url, is_local_source=False):
    channels = []
    print(f"Fetching {url}... ", end="", flush=True)
    try:
        with requests.get(url, headers=HEADERS, timeout=10, stream=True) as resp:
            resp.raise_for_status()
            attrs = {}
            name = None
            current_cat = None

            for line in resp.iter_lines(decode_unicode=True):
                if not line: continue
                line = line.strip()

                if line.startswith("#EXTINF"):
                    name_str = line.rsplit(',', 1)[-1].strip()
                    category = get_category(name_str, is_local_source)

                    if category:
                        name = name_str
                        current_cat = category
                        attrs = {}
                        for match in re.finditer(r'(\S+)="(.*?)"', line):
                            attrs[match.group(1)] = match.group(2)
                    else:
                        name = None

                elif not line.startswith("#") and name:
                    if line.startswith("http"):
                        normalized_name = clean_name(name).lower()
                        channels.append((line, current_cat, attrs, name, normalized_name))
                    name = None

        print(f"OK (Found {len(channels)} targets)")
    except Exception as e:
        print(f"FAIL ({e})")

    return channels

def get_working_link(channel_group):
    for channel_data in channel_group:
        url = channel_data[0]
        try:
            r = requests.get(url, headers=HEADERS, timeout=6, stream=True)
            r.close()
            if r.status_code < 400:
                return channel_data
        except Exception:
            pass
    return None

def main():
    old_playlist = None
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            old_playlist = f.read()

    raw_channels = []
    for source in SOURCES_GENERAL:
        raw_channels.extend(fetch_channels(source, is_local_source=False))
    for source in SOURCES_LOCAL:
        raw_channels.extend(fetch_channels(source, is_local_source=True))

    # Group by name for dedupe
    channels_by_name = {}
    for ch in raw_channels:
        normalized_name = ch[4]
        if normalized_name not in channels_by_name:
            channels_by_name[normalized_name] = []
        channels_by_name[normalized_name].append(ch)

    print(f"\nTotal unique channels to test: {len(channels_by_name)}")
    print("Testing streams with 6s timeout...\n")

    valid_channels = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(get_working_link, channels_by_name.values())
        for res in results:
            if res is not None:
                valid_channels.append(res)

    output = {cat: [] for cat in CATEGORIES}
    for url, cat, attrs, ch_name, normalized_name in valid_channels:
        new_attrs = dict(attrs)
        new_attrs["group-title"] = cat
        output[cat].append((ch_name, url, new_attrs))

    for cat in output:
        output[cat].sort(key=lambda x: x[0].lower())

    total = sum(len(v) for v in output.values())

    if total == 0:
        print("\n⚠️ No valid channels found. Restoring previous playlist.")
        if old_playlist:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(old_playlist)
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cat in CATEGORIES:
            if not output[cat]:
                continue
            f.write(f"\n# --- {cat} ---\n")
            for ch_name, url, attrs in output[cat]:
                extinf = '#EXTINF:-1'
                for k, v in attrs.items():
                    extinf += f' {k}="{v}"'
                extinf += f',{ch_name}'
                f.write(extinf + '\n')
                f.write(url + '\n')

    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        f.write(open(OUTPUT_FILE).read())

    print(f"\n✅ Playlist created: {total} live working Tamil + English channels")
    for cat in CATEGORIES:
        if output[cat]:
            print(f" {cat}: {len(output[cat])}")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("# 📺 Tamil & English IPTV\n\n")
        f.write(f"**Updated:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n\n")
        f.write(f"**Live, Working Channels:** {total}\n\n")
        f.write("| Category | Channels |\n| --- | --- |\n")
        for cat in CATEGORIES:
            if output[cat]:
                f.write(f"| {cat} | {len(output[cat])} |\n")

if __name__ == "__main__":
    main()
