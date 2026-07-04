import requests
import re
import time
import os
from collections import OrderedDict

OUTPUT_FILE = "playlist.m3u"
BACKUP_FILE = "playlist_backup.m3u"

SOURCES = [
    "https://raw.githubusercontent.com/Vmfm/tamilvmtv/main/live/channels.m3u",
    "https://raw.githubusercontent.com/Vmfm/tamilvmtv/main/live/jio.m3u",
    "https://raw.githubusercontent.com/Tamilwebcast/Tamilwebcast.github.io/main/TWCIPTV.m3u",
    "https://raw.githubusercontent.com/Indiblog/india-iptv/main/output/india_iptv.m3u",
    "https://raw.githubusercontent.com/Indiblog/india-iptv/main/output/india_general.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/jtv.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/pishow.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/yupptvfast.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/tangotv.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/ashokadigital.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/neotv.m3u",
    "https://iptv-org.github.io/iptv/languages/tam.m3u",
    "https://iptv-org.github.io/iptv/languages/eng.m3u"
]

CATEGORIES = [
    "Tamil Entertainment", "Tamil News", "Tamil Movies", "Tamil Music",
    "Tamil Kids", "Tamil Sports", "Tamil Devotional", "Tamil Infotainment",
    "Tamil Shopping", "Tamil Local", "English Movies", "English News"
]

# Using tuples for slightly faster iteration during checking
TAMIL_KW = (
    "tamil", "sun ", "vijay", "kalaignar", "jaya ", "raj ", "captain",
    "polimer", "mega ", "pudhiya", "thanthi", "vasanth", "isaiaruvi",
    "k tv", "ktv", "adithya", "chutti", "chithiram", "makkal", "sirippoli",
    "vendhar", "peppers", "angel", "murugan", "madha", "velicham", "seithigal",
    "podhigai", "puthiya", "thalaimurai", "sathiyam", "madhimugam",
    "aruloli", "jeevan", "nambikkai", "shubhsandesh", "aastha"
)

ENGLISH_KW = (
    "english", "hbo", "cnn", "bbc", "disney", "discovery", "nat geo",
    "sony pix", "star movies", "mn+", "hits", "romedy", "comedy central",
    "axn", "colors infinity", "zee café", "&flix", "&privé", "star world",
    "fox", "fyi", "tlc", "animal planet", "history tv18", "bloomberg",
    "movies now", "sky news", "ndtv", "wion", "times now"
)

BLOCKED = (
    "telugu", "hindi", "marathi", "malayalam", "kannada", "bengali", "punjabi",
    "gujarati", "oriya", "assamese", "bhojpuri", "urdu", "sanskrit",
    "etv", "gemini", "maa tv", "tv9", "zee marathi", "star pravah",
    "asianet", "kiran", "flowers", "mazhavil", "kairali", "amrita",
    "sangeet", "b4u", "aaj tak", "sony sab", "sony pal",
    "star plus", "zee tv", "star utsav", "star gold", "sony max",
    "dangal", "big magic", "dd national", "dd india", "sony max 2",
    "colors kannada", "colors bangla", "colors gujarati", "colors marathi"
)

MASTER_LIST = {
    "sun tv": "Tamil Entertainment", "star vijay": "Tamil Entertainment", "zee tamil": "Tamil Entertainment",
    "colors tamil": "Tamil Entertainment", "kalaignar tv": "Tamil Entertainment", "raj tv": "Tamil Entertainment",
    "polimer tv": "Tamil Entertainment", "mega tv": "Tamil Entertainment", "vasanth tv": "Tamil Entertainment",
    "puthuyugam tv": "Tamil Entertainment", "captain tv": "Tamil Entertainment", "adithya tv": "Tamil Entertainment",
    "vendhar tv": "Tamil Entertainment", "jaya tv": "Tamil Entertainment", "d tamil": "Tamil Entertainment",
    "sirippoli": "Tamil Entertainment", "dd tamil": "Tamil Entertainment", "sun news": "Tamil News",
    "raj news": "Tamil News", "thanthi tv": "Tamil News", "news18 tamil": "Tamil News", "polimer news": "Tamil News",
    "news7 tamil": "Tamil News", "news j": "Tamil News", "kalaignar seithigal": "Tamil News", "win news": "Tamil News",
    "sathiyam tv": "Tamil News", "madhimugam tv": "Tamil News", "pudhiya thalaimurai": "Tamil News",
    "zee tamil news": "Tamil News", "ktv": "Tamil Movies", "zee thirai": "Tamil Movies", "sun life": "Tamil Movies",
    "raj digital plus": "Tamil Movies", "jaya movie": "Tamil Movies", "vijay super": "Tamil Movies",
    "j movies": "Tamil Movies", "thirai tv": "Tamil Movies", "boktv": "Tamil Movies", "ducktv": "Tamil Movies",
    "ktv 2": "Tamil Movies", "ktv sport": "Tamil Movies", "talktv": "Tamil Movies", "sun music": "Tamil Music",
    "raj musix": "Tamil Music", "isaiaruvi": "Tamil Music", "g music": "Tamil Music", "jcv musix": "Tamil Music",
    "chutti tv": "Tamil Kids", "chithiram tv": "Tamil Kids", "cartoon network tamil": "Tamil Kids",
    "pogo tamil": "Tamil Kids", "nick tamil": "Tamil Kids", "sony yay tamil": "Tamil Kids", "star sports tamil": "Tamil Sports",
    "angel tv": "Tamil Devotional", "murugan tv": "Tamil Devotional", "discovery tamil": "Tamil Infotainment",
    "sony bbc earth": "Tamil Infotainment", "bbc earth": "Tamil Infotainment", "aastha tamil": "Tamil Local",
    "kalaignar murasu": "Tamil Local", "madha tv": "Tamil Local", "makkal tv": "Tamil Local", "news 7 tamil": "Tamil Local",
    "peppers tv": "Tamil Local", "puthiya thalaimurai": "Tamil Local", "tamilan tv": "Tamil Local",
    "tamilvision-tv": "Tamil Local", "thanthi one": "Tamil Local", "velicham tv": "Tamil Local", "vijay takkar": "Tamil Local",
    "afroturk tv": "Tamil Local", "albuk tv": "Tamil Local", "ark tv": "Tamil Local", "baby shark tv": "Tamil Local",
    "bek news": "Tamil Local", "bek sports": "Tamil Local", "cbs news los angeles": "Tamil Local", "hktv": "Tamil Local",
    "island luck tv": "Tamil Local", "krca-tv": "Tamil Local", "la36": "Tamil Local", "mindanow network tv": "Tamil Local",
    "montreal greek tv": "Tamil Local", "ncis: los angeles": "Tamil Local", "spark tv": "Tamil Local", "stryk tv": "Tamil Local",
    "the walk tv": "Tamil Local", "cnn": "English News", "bbc news": "English News", "bloomberg": "English News",
    "ndtv 24x7": "English News", "wion": "English News", "times now": "English News", "sky news": "English News",
    "euronews english": "English News", "fox news": "English News", "africanews english": "English News",
    "acnn": "English News", "france 24 english": "English News", "al jazeera english": "English News",
    "alarabiya english": "English News", "dw english": "English News", "rt documentary": "English News",
    "telesur english": "English News", "ntd tv english": "English News", "bloomberg originals": "English News",
    "hbo": "English Movies", "star movies": "English Movies", "sony pix": "English Movies", "mn+": "English Movies",
    "&flix": "English Movies", "romedy now": "English Movies", "comedy central": "English Movies",
    "disney channel": "English Movies", "disney junior": "English Movies", "disney xd": "English Movies",
    "axn": "English Movies", "fox": "English Movies", "bbc america": "English Movies", "bbc food": "English Movies",
    "bbc home & garden": "English Movies", "bbc lifestyle": "English Movies", "colors infinity": "English Movies",
    "ndtv good times": "English Movies", "ndtv profit": "English Movies", "ndtv lanka": "English Movies",
    "3abn": "English Movies", "africa 24 english": "English Movies", "afrolandtv": "English Movies",
    "chosen tv english": "English Movies", "god stands": "English Movies", "hope channel": "English Movies",
    "ifilm english": "English Movies", "livenow from fox": "English Movies", "logos tv english": "English Movies",
    "madani channel english": "English Movies", "marjaeyat tv english": "English Movies", "noursat english": "English Movies",
    "peace tv english": "English Movies", "real madrid tv english": "English Movies", "stingray": "English Movies",
    "sumtv english": "English Movies", "terra mater wild": "English Movies", "tv brics english": "English Movies",
    "tv maná english": "English Movies", "xite hits": "English Movies", "filmbox+": "English Movies"
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean_name(raw):
    raw = re.sub(r'\s*\[.*?\]\s*', '', raw)
    raw = re.sub(r'\s*\(.*?\)\s*', '', raw)
    raw = re.sub(r'\s*\b(HD|SD|HEVC|4K|UHD|HDR|Dolby)\b\s*', '', raw, flags=re.I)
    return ' '.join(raw.split()).strip()

def get_category(name, lang, group_title=""):
    clean = clean_name(name).lower()

    if group_title:
        gt_lower = group_title.lower()
        if lang == "tamil" and gt_lower.startswith("tamil"):
            for cat in CATEGORIES:
                if cat.lower() == gt_lower:
                    return cat
        elif lang == "english" and gt_lower.startswith("english"):
            for cat in CATEGORIES:
                if cat.lower() == gt_lower:
                    return cat

    for master_name, category in MASTER_LIST.items():
        if master_name in clean or clean in master_name:
            return category

    if lang == "tamil":
        if any(k in clean for k in ("news", "seithigal")): return "Tamil News"
        if any(k in clean for k in ("movie", "cinema", "thirai")): return "Tamil Movies"
        if any(k in clean for k in ("music", "isai")): return "Tamil Music"
        if any(k in clean for k in ("kids", "children", "chutti")): return "Tamil Kids"
        if any(k in clean for k in ("sport", "cricket", "football")): return "Tamil Sports"
        if any(k in clean for k in ("devotional", "spiritual", "angel", "murugan")): return "Tamil Devotional"
        if any(k in clean for k in ("infotainment", "discovery", "bbc", "earth")): return "Tamil Infotainment"
        return "Tamil Local"
    else:
        if "news" in clean:
            return "English News"
        return "English Movies"

def fetch_channels(url):
    channels = []
    print(f"Fetching {url} ... ", end="", flush=True)
    try:
        # stream=True ensures we don't load huge files entirely into memory at once
        with requests.get(url, headers=HEADERS, timeout=15, stream=True) as resp:
            resp.raise_for_status()
            
            attrs = {}
            name = None
            current_lang = None
            
            # Read line by line on the fly
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                
                line = line.strip()
                
                if line.startswith("#EXTINF"):
                    # Extract just the name portion quickly
                    name_str = line.rsplit(',', 1)[-1].strip()
                    name_lower = name_str.lower()
                    
                    # 1. FAST BLOCK: Throw away immediately if it contains blocked words
                    if any(b in name_lower for b in BLOCKED):
                        name = None
                        continue
                        
                    # 2. FAST MATCH: Check language immediately without full parsing
                    lang = None
                    if any(kw in name_lower for kw in TAMIL_KW):
                        lang = "tamil"
                    elif any(kw in name_lower for kw in ENGLISH_KW):
                        lang = "english"
                        
                    # If it's neither Tamil nor English, skip it entirely
                    if not lang:
                        name = None
                        continue
                        
                    # ONLY if it passes the checks above do we run the heavy Regex
                    attrs = {}
                    for match in re.finditer(r'(\S+)="(.*?)"', line):
                        attrs[match.group(1)] = match.group(2)
                    name = name_str
                    current_lang = lang

                elif not line.startswith("#") and name:
                    if line.startswith("http"):
                        group = attrs.get("group-title", "")
                        cat = get_category(name, current_lang, group)
                        if cat is None:
                            cat = "Tamil Local" if current_lang == "tamil" else "English Movies"
                        channels.append((cat, attrs, name, line))
                    name = None
                    
        print(f"OK (Found {len(channels)})")
    except Exception as e:
        print(f"FAIL ({e})")
    
    return channels

def main():
    old_playlist = None
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            old_playlist = f.read()

    all_channels = []
    for source in SOURCES:
        all_channels.extend(fetch_channels(source))

    output = {cat: OrderedDict() for cat in CATEGORIES}
    seen = set()
    
    for cat, attrs, raw_name, url in all_channels:
        if url in seen:
            continue
        seen.add(url)
        new_attrs = dict(attrs)
        new_attrs["group-title"] = cat
        output[cat][url] = (new_attrs, raw_name)

    total = sum(len(v) for v in output.values())
    if total == 0:
        print("\n⚠️ No valid channels found. Restoring previous playlist.")
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
