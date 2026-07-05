import requests
import re
import json
import datetime
import concurrent.futures

# ==========================================
# 1. USER'S CUSTOM HARDCODED CHANNELS
# ==========================================
USER_CUSTOM_CHANNELS = """
#EXTINF:-1 group-title="local channels",Sana TV
https://galaxyott.live/hls/sanatv.m3u8
#EXTINF:-1 group-title="local channels",Sana Plus
https://galaxyott.live/hls/sanaplus.m3u8
#EXTINF:-1 group-title="local channels",UTV
https://stream.galaxyott.live/live/utv/index.m3u8
#EXTINF:-1 group-title="local channels",NTV
https://galaxyott.live/hls/ntv.m3u8
#EXTINF:-1 group-title="local channels",Surya TV
https://galaxyott.live/hls/suryatv.m3u8
#EXTINF:-1 group-title="local channels",Subin TV
https://stream.galaxyott.live/live/subintv/index.m3u8
#EXTINF:-1 group-title="local channels",Moon TV
https://live.maxtn.in/moontv/moontv/index.m3u8
#EXTINF:-1 group-title="local channels",Sakthi TV
https://live.sscloud7.in/live/sakthitv/index.m3u8
#EXTINF:-1 group-title="local channels",Prime TV
https://live.applelive.in/primetv/primetv/index.m3u8
#EXTINF:-1 group-title="local channels",D TV
https://stream.d6-pro.com/Dtv/live/index.m3u8
#EXTINF:-1 group-title="local channels",TDN
https://live.maxtn.in/tdn/tdn/index.m3u8
#EXTINF:-1 group-title="local channels",7 Green
https://account33.livebox.co.in/7GREEN4Khls/live.m3u8
#EXTINF:-1 group-title="local channels",Yet TV
https://live.yettelevision.com:5443/LiveApp/streams/yettv.m3u8
#EXTINF:-1 group-title="local channels",PR TV
https://play.applelive.in/prtv/prtv.m3u8
#EXTINF:-1 group-title="local channels",Riya TV
https://play.applelive.in/riyatv/riyatv.m3u8
#EXTINF:-1 group-title="local channels",Dark TV
https://play.applelive.in/darktv/darktv.m3u8
#EXTINF:-1 group-title="local channels",Harin TV HD
https://ipcloud.live/harintv/harintvhd/index.m3u8
#EXTINF:-1 group-title="local channels",Phoenix TV
https://stream.onecloudlive.in/phoenixtv/phoenixtv/index.m3u8
#EXTINF:-1 group-title="local channels",Roja TV
https://live.rojatv.cloud/rojatv/rojatv/index.m3u8
#EXTINF:-1 group-title="local channels",Roja TV
https://stream.rojatv.cloud/rojatv/rojatv/index.m3u8
#EXTINF:-1 group-title="local channels",Nila TV
https://live.olidigital.in/nilatv/nilatv/index.m3u8
#EXTINF:-1 group-title="local channels",SMCV TV
https://singamcloud.in/smcvtv/smcvtv/index.m3u8
#EXTINF:-1 group-title="local channels",APS TV
https://apstv-a1.tamilstream.in/apstv/apstv/index.m3u8
#EXTINF:-1 group-title="local channels",APS Gold
https://apsgold-a1.tamilstream.in/apsgold/apsgold/index.m3u8
#EXTINF:-1 group-title="local channels",MTV Men HD
https://ipcloud.live/mtv/menhd/index.m3u8
#EXTINF:-1 group-title="local channels",MSN TV
https://ipcloud.live/msntv/msntv/index.m3u8
#EXTINF:-1 group-title="local channels",Veerali TV
https://ipcloud.live/veerali/veeralitv/index.m3u8
#EXTINF:-1 group-title="local channels",Three Star TV HD
https://stream.onecloudlive.in/threestartv/threestarhd/index.m3u8
#EXTINF:-1 group-title="local channels",Shalini TV
https://ipcloud.live/shalinitv/shalinitv/index.m3u8
#EXTINF:-1 group-title="local channels",JCV TV
https://play.applelive.in/jcvtv/jcvtv.m3u8
#EXTINF:-1 group-title="local channels",JCV Musix
https://play.applelive.in/jcvtv/jcvmusix.m3u8
#EXTINF:-1 group-title="local channels",Thendral TV
https://live.thendralcloud.in/thendraltv/d0dbe915091d400bd8ee7f27f0791303.sdp/chunks.m3u8
#EXTINF:-1 group-title="local channels",Anbu TV HD
https://ipcloud.live/anbutv/anbutvhd/index.m3u8
#EXTINF:-1 group-title="local channels",Nellai TV
https://stream.onecloudlive.in/nellaitv/nellaitv/index.m3u8
#EXTINF:-1 group-title="local channels",A3e0b02f
https://app.ashokadigital.net/app/a3e0b02f/index.m3u8
#EXTINF:-1 group-title="local channels",Akash TV
https://account2.livebox.co.in/AkashTvhls/live.m3u8
#EXTINF:-1 group-title="local channels",Apple TV
https://play.applelive.in/appletv/appletv.m3u8
#EXTINF:-1 group-title="local channels",Jeyson TV
https://play.applelive.in/jeysontv/jeysontv.m3u8
#EXTINF:-1 group-title="local channels",JJ Max
https://play.applelive.in/jjmax/jjmax.m3u8
#EXTINF:-1 group-title="local channels",JC TV
https://play.applelive.in/jctv/jctv.m3u8
#EXTINF:-1 group-title="local channels",Digital TV
https://play.applelive.in/digitaltv/digitaltv.m3u8
#EXTINF:-1 group-title="local channels",Oscar TV
https://account21.livebox.co.in/oscartvhls/live.m3u8
#EXTINF:-1 group-title="local channels",Jeyan TV
https://stream.onecloudlive.in/jeyantv/jeyantv/index.m3u8
#EXTINF:-1 group-title="local channels",Vidyal TV
https://account11.livebox.co.in/vidyaltvhls/live.m3u8?psk=stream
#EXTINF:-1 group-title="local channels",KCN TV
https://view.rcserver.in/tmp_hls12/kcntv/index.m3u8
#EXTINF:-1 group-title="local channels",Sky TV
https://sscloud7.com/live/skytv/index.m3u8
#EXTINF:-1 group-title="local channels",Boys TV
https://rtmp.applelive.in/boystv/boystv/index.m3u8
#EXTINF:-1 group-title="local channels",King TV
https://server.sscloud7.in/kingtv/kingtv/index.m3u8
#EXTINF:-1 group-title="local channels",Sky TV
https://view.rcserver.in/tmp_hls6/skytv/index.m3u8
#EXTINF:-1 group-title="local channels",Udhayam TV
https://view.rcserver.in/tmp_hls8/udhayamtv/index.m3u8
#EXTINF:-1 group-title="local channels",TN TV
https://view.rcserver.in/tmp_hls14/tntv/index.m3u8
#EXTINF:-1 group-title="local channels",Senthamil TV
https://view.rcserver.in/tmp_hls24/senthamiltv/index.m3u8
#EXTINF:-1 group-title="local channels",Karur TV
https://view.rcserver.in/tmp_hls16/karurtv/index.m3u8
#EXTINF:-1 group-title="local channels",Karur City
https://view.rcserver.in/tmp_hls17/karurcity/index.m3u8
#EXTINF:-1 group-title="local channels",Tmp Hls20
https://view.rcserver.in/tmp_hls20/index.m3u8
#EXTINF:-1 group-title="local channels",Thirai TV
https://view.apserver.in/tmp_hls2/thiraitv/index.m3u8
#EXTINF:-1 group-title="local channels",Bharathi TV
https://server.sscloud7.in/live/bharathitv/index.m3u8
#EXTINF:-1 group-title="local channels",Thendral TV
https://sscloud7.com/live/thendraltv/index.m3u8
#EXTINF:-1 group-title="local channels",Irattipaathai TV
https://account31.livebox.co.in/IRATTAIPAATHAITVhls/live.m3u8
#EXTINF:-1 group-title="local channels",MCN TV
https://play.applelive.in/mcntv/mcntv.m3u8
#EXTINF:-1 group-title="local channels",STN TV
https://play.applelive.in/stntv/stntv.m3u8
#EXTINF:-1 group-title="local channels",Suriyan TV
https://view.rcserver.in/tmp_hls9/suriyantv/index.m3u8
#EXTINF:-1 group-title="local channels",Vasanth TV
https://play.applelive.in/vasanthtv/vasanthtv.m3u8
#EXTINF:-1 group-title="local channels",Eesan TV
https://live.singamcloud.in/eesantv/eesantv/index.m3u8
#EXTINF:-1 group-title="local channels",68b001a0
https://app.ashokadigital.net/app/68b001a0/index.m3u8
#EXTINF:-1 group-title="local channels",Jeyam TV
https://live.sscloud7.in/live/jeyamtv/index.m3u8
#EXTINF:-1 group-title="local channels",Aadhavan TV Colours
https://live.olidigital.in/aadhavantvcolours/aadhavantvcolours/index.m3u8
#EXTINF:-1 group-title="local channels",Solai TV HD
https://ipcloud.live/solaitv/solaihd/index.m3u8
#EXTINF:-1 group-title="local channels",MM TV Jeyam Plus
https://ipcloud.live/mmtv/jeyamplus/index.m3u8
#EXTINF:-1 group-title="tamil iptv channels",chithiram tv
https://cdn-6.pishow.tv/live/1243/master.m3u8
#EXTINF:-1 group-title="tamil iptv channels",dd tamil
https://d2lk5u59tns74c.cloudfront.net/out/v1/abf46b14847e45499f4a47f3a9afe93d/index.m3u8
#EXTINF:-1 group-title="tamil iptv channels",EET Live EET TV
https://eu.streamjo.com/eetlive/eettv.m3u8
#EXTINF:-1 group-title="tamil iptv channels",EET Live EET TV
https://live.streamjo.com/eetlive/eettv.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Isaiaruvi
https://segment.yuppcdn.net/140622/isaiaruvi/playlist.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Murasu
https://segment.yuppcdn.net/050522/murasu/playlist.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Kalaignar TV
https://segment.yuppcdn.net/240122/kalaignartv/playlist.m3u8
#EXTINF:-1 group-title="tamil iptv channels",mathimugam
https://cdn-3.pishow.tv/live/1476/master.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Makkal
https://5k8q87azdy4v-hls-live.wmncdn.net/MAKKAL/271ddf829afeece44d8732757fba1a66.sdp/playlist.m3u8
#EXTINF:-1 group-title="tamil iptv channels",malai murasu
https://cdn-3.pishow.tv/live/1606/master.m3u8
#EXTINF:-1 group-title="tamil iptv channels",News7
https://segment.yuppcdn.net/240122/news7/playlist.m3u8
#EXTINF:-1 group-title="tamil iptv channels",News18 Tamil Nadu NW18
https://n18syndication.akamaized.net/bpk-tv/News18_Tamil_Nadu_NW18_MOB/output01/master.m3u8
#EXTINF:-1 group-title="tamil iptv channels",news j
https://cdn-3.pishow.tv/live/1279/master.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Polimer News
https://segment.yuppcdn.net/110322/polimernews/playlist.m3u8
#EXTINF:-1 group-title="tamil iptv channels",polimer tv
https://cdn-2.pishow.tv/live/1241/master.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Puthiya
https://segment.yuppcdn.net/240122/puthiya/playlist.m3u8
#EXTINF:-1 group-title="tamil iptv channels",raj tv
https://d3qs3d2rkhfqrt.cloudfront.net/out/v1/2839e3d1e0f84a2e821c1708d5fdfdf0/index.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Roja TV
https://stream.rojatv.cloud/rojatv/rojatv/index.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Roja TV
https://live.rojatv.cloud/rojatv/rojatv/index.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Sana Plus
https://galaxyott.live/hls/sanaplus.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Sana TV
https://galaxyott.live/hls/sanatv.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Siripoli
https://segment.yuppcdn.net/240122/siripoli/playlist.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Subin TV
https://stream.galaxyott.live/live/subintv/index.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Zionmediait 97484f5ce6da96e496a9b87c439835d0
https://cdn.zionmediait.com/zionmediaitserver2024/97484f5ce6da96e496a9b87c439835d0.sdp/playlist.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Thalaa TV TAM
https://streams2.sofast.tv/ptnr-yupptv/title-THALAA-TV-TAM_yupptv/v1/master/611d79b11b77e2f571934fd80ca1413453772ac7/2069c593-3c07-4d62-9d44-746be5c3a5d6/manifest.m3u8
#EXTINF:-1 group-title="tamil iptv channels",thanthi tv
https://cdn-3.pishow.tv/live/1612/master.m3u8
#EXTINF:-1 group-title="tamil iptv channels",Thendral TV
https://live.thendralcloud.in/thendraltv/d0dbe915091d400bd8ee7f27f0791303.sdp/chunks.m3u8
#EXTINF:-1 group-title="tamil iptv channels",vendhar tv
https://cdn-3.pishow.tv/live/1271/master.m3u8
#EXTINF:-1 group-title="tamil iptv channels",win news
https://cdn-4.pishow.tv/live/1531/master.m3u8
"""

# ==========================================
# 2. ALL YOUR SOURCES
# ==========================================
SOURCES = [
    "https://raw.githubusercontent.com/Vmfm/tamilvmtv/main/live/channels.m3u",
    "https://raw.githubusercontent.com/Vmfm/tamilvmtv/main/live/jio.m3u",
    "https://raw.githubusercontent.com/Tamilwebcast/Tamilwebcast.github.io/main/TWCIPTV.m3u",
    "https://raw.githubusercontent.com/PraveenBojja83/praveentv/main/resource/channels.json",
    "https://raw.githubusercontent.com/Indiblog/india-iptv/main/output/india_iptv.m3u",
    "https://raw.githubusercontent.com/Indiblog/india-iptv/main/output/india_general.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/jtv.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/pishow.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/yupptvfast.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/tangotv.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/ashokadigital.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/neotv.m3u",
    "https://raw.githubusercontent.com/amazeyourself/tamil-local-iptv/refs/heads/main/channels.m3u",
    "https://iptv-org.github.io/iptv/languages/tam.m3u",
    "https://iptv-org.github.io/iptv/languages/eng.m3u"
]

LOCAL_SOURCES = [
    "https://raw.githubusercontent.com/Vmfm/tamilvmtv/main/live/channels.m3u",
    "https://raw.githubusercontent.com/amazeyourself/m3u/main/ashokadigital.m3u",
    "https://raw.githubusercontent.com/amazeyourself/tamil-local-iptv/refs/heads/main/channels.m3u"
]

# ==========================================
# 3. STRICT CATEGORY WHITELIST & ORDERING
# ==========================================
CATEGORY_ORDER = [
    "local channels",
    "tamil iptv channels",
    "Tamil Local Channels",
    "Tamil GEC",
    "Tamil Movies",
    "Tamil News",
    "Tamil Comedy",
    "Tamil Music",
    "Tamil Infotainment",
    "Tamil Spiritual",
    "Tamil Kids",
    "English GEC",
    "English Movies",
    "English National News",
    "English International News",
    "English Business News",
    "English Infotainment",
    "English Lifestyle",
    "English Kids",
    "Sports"
]

CATEGORIES = {
    # ---------------- TAMIL ----------------
    "Tamil GEC": ["sun tv", "star vijay", "vijay tv", "zee tamil", "colors tamil", "kalaignar tv", "kalaignar", "jaya tv", "raj tv", "polimer tv", "makkal tv", "vasanth tv", "vasanth", "puthuyugam tv", "puthuyugam", "mega tv", "captain tv", "vendhar tv", "vendhar"],
    "Tamil Movies": ["ktv", "star vijay super", "vijay super", "zee thirai", "j movie", "jaya movie", "raj digital plus", "murasu", "mega 24", "sun action"],
    "Tamil News": ["sun news", "puthiya thalaimurai", "thanthi tv", "news18 tamil", "polimer news", "news7 tamil", "sathiyam", "news j", "jaya plus", "kalaignar seithigal", "raj news", "captain news"],
    "Tamil Comedy": ["adithya tv", "sirippoli"],
    "Tamil Music": ["sun music", "star vijay music", "vijay music", "isaiaruvi", "isai aruvi", "jaya max", "raj musix", "mega musiq"],
    "Tamil Infotainment": ["sun life", "discovery tamil", "nat geo tamil", "sony bbc earth tamil", "bbc earth tamil"],
    "Tamil Spiritual": ["madha tv", "angel tv", "nambikkai", "vaanavil", "jothi tv", "velicham tv", "sankara tv", "sri sankara"],
    "Tamil Kids": ["chutti tv", "etv bal bharat tamil", "cartoon network tamil", "pogo tamil", "discovery kids tamil", "sony yay tamil", "nick tamil", "disney tamil", "kochu tv"],
    
    # ---------------- ENGLISH ----------------
    "English GEC": ["zee cafe", "colors infinity", "comedy central", "disney international"],
    "English Movies": ["star movies", "sony pix", "movies now", "mnx", "mn+", "&flix", "&prive", "romedy now", "hbo", "wb"],
    "English National News": ["times now", "republic tv", "cnn-news18", "india today", "ndtv 24x7", "newsx", "mirror now", "wion"],
    "English International News": ["bbc news", "cnn international", "al jazeera", "rt news", "russia today", "rt "],
    "English Business News": ["cnbc-tv18", "et now", "ndtv profit"],
    "English Infotainment": ["discovery channel", "national geographic", "history tv18", "animal planet", "sony bbc earth"],
    "English Lifestyle": ["tlc", "travelxp", "goodtimes"],
    "English Kids": ["cartoon network", "nickelodeon", "pogo", "disney channel", "disney junior", "sonic", "super hungama", "discovery kids", "babytv"],
    
    # ---------------- SPORTS ----------------
    "Sports": ["star sports 1", "star sports 2", "star sports select 1", "star sports select 2", "sony sports ten 1", "sony sports ten 2", "sony sports ten 5", "sony ten 1", "sony ten 2", "sony ten 5", "eurosport", "sports18", "sports 18"],
    
    # ---------------- LOCAL ----------------
    "Tamil Local Channels": ["local", "cable", "arun", "network"]
}

# Strict filter using regex boundaries to drop "KTV Bangla" or "Star Sports Hindi"
BLOCKED_WORDS = ["bangla", "telugu", "hindi", "marathi", "malayalam", "kannada", "bengali", "punjabi", "gujarati", "bhojpuri", "urdu", "oriya", "assamese", "arabic", "spanish", "french"]


# ==========================================
# 4. CORE FUNCTIONS
# ==========================================
def clean_name(name):
    name = re.sub(r'\s*\[.*?\]\s*', '', name)
    name = re.sub(r'\s*\(.*?\)\s*', '', name)
    return ' '.join(name.split()).strip()

def get_core_name(name):
    """
    Creates a strict "Core Name" to perfectly deduplicate identical channels.
    Example: 'Sun TV HD' -> 'suntv'
    """
    n = re.sub(r'\s*\[.*?\]\s*', '', name)
    n = re.sub(r'\s*\(.*?\)\s*', '', n)
    n = re.sub(r'\b(HD|SD|FHD|4K|UHD|1080p|720p|Premium|IN)\b', '', n, flags=re.I)
    n = re.sub(r'[^a-zA-Z0-9]', '', n)
    return n.lower()

def get_category(name):
    if not name: return None
    n = name.lower()
    
    # 1. Regex boundary block to stop "KTV Bangla" from passing
    for blocked in BLOCKED_WORDS:
        if re.search(r'\b' + blocked + r'\b', n):
            return None
            
    # 2. Priority Matching: Find the LONGEST keyword match to prevent overlapping categories.
    # (e.g. "Star Vijay Super" matches Movies instead of matching "Star Vijay" and falling into GEC)
    best_match_cat = None
    best_match_len = 0
    
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            # Check if the keyword exists as an exact word, or is a direct substring
            if re.search(r'\b' + re.escape(kw) + r'\b', n) or kw in n:
                if len(kw) > best_match_len:
                    best_match_len = len(kw)
                    best_match_cat = cat
                    
    return best_match_cat

def parse_m3u(content):
    channels = []
    lines = content.splitlines()
    current_name, current_logo, current_cat = None, "", None
    for line in lines:
        line = line.strip()
        if line.startswith("#EXTINF:"):
            logos = re.findall(r'tvg-logo="(.*?)"', line)
            current_logo = logos[0] if logos else ""
            
            cats = re.findall(r'group-title="(.*?)"', line)
            current_cat = cats[0] if cats else None
            
            current_name = line.rsplit(',', 1)[1].strip() if ',' in line else None
        elif line and not line.startswith("#") and current_name:
            channels.append((current_name, current_logo, line, current_cat))
            current_name = None
            current_cat = None
    return channels

def parse_json(content):
    channels = []
    try:
        data = json.loads(content)
        items = data if isinstance(data, list) else data.get('channels', data.get('streams', data.get('data', [])))
        for item in items:
            name = item.get('name') or item.get('title') or item.get('channel_name')
            url = item.get('url') or item.get('stream') or item.get('link') or item.get('channel_url')
            logo = item.get('logo') or item.get('icon') or item.get('stream_icon') or ""
            if name and url: channels.append((name, logo, url, None))
    except Exception: pass
    return channels

def check_stream_group(channel_group):
    """
    DEEP PACKET INSPECTION: Checks duplicates sequentially. EVERY CHANNEL is checked.
    Destroys fake 200 OK HTML/JSON pages. Returns the FIRST authentic stream.
    """
    headers = {
        'User-Agent': 'VLC/3.0.16 LibVLC/3.0.16', # Standard TV Player agent to avoid blocks
        'Accept': '*/*'
    }
    
    for item in channel_group:
        orig_name, logo, url, cat = item
        
        try:
            # 5s connect, 10s read timeout to prevent dropping slow but working links
            response = requests.get(url, headers=headers, timeout=(5.0, 10.0), stream=True, allow_redirects=True)
            
            if response.status_code in [200, 302]:
                content_type = response.headers.get('Content-Type', '').lower()
                
                # Instantly drop JSON/HTML pages masquerading as streams
                if 'application/json' in content_type or 'text/html' in content_type:
                    continue
                
                chunk = response.raw.read(1024)
                if not chunk: continue
                
                text_chunk = chunk.decode('utf-8', errors='ignore').lower()
                
                # Deep payload inspection to catch hidden error pages
                if '<html' in text_chunk or '<!doctype' in text_chunk or '<body' in text_chunk:
                    continue
                if text_chunk.strip().startswith('{') and '}' in text_chunk:
                    continue
                    
                # Strict validation for M3U8 vs generic media streams
                is_media = any(v in content_type for v in ['video/', 'audio/', 'octet-stream', 'mpeg', 'application/vnd.apple.mpegurl'])
                is_m3u8 = '#extm3u' in text_chunk or '#ext-x' in text_chunk
                
                if is_media or is_m3u8:
                    return item # Passes all strict tests!
        except Exception:
            pass
            
    return None

# ==========================================
# 5. MAIN EXECUTION
# ==========================================
def main():
    print("Starting Strictly Categorized, Sorted, & Fast Playlist Builder...")
    
    grouped_channels = {} 
    seen_urls = set()

    # --- INJECT USER CUSTOM CHANNELS ---
    print("\nParsing User Custom Channels...")
    custom_parsed = parse_m3u(USER_CUSTOM_CHANNELS)
    for name, logo, url, custom_cat in custom_parsed:
        url = url.strip()
        if not url.startswith("http") or url in seen_urls: continue
        seen_urls.add(url)
        
        cat = custom_cat if custom_cat else "tamil iptv channels"
        clean_n = clean_name(name)
        core_n = get_core_name(name)
        
        if core_n not in grouped_channels:
            grouped_channels[core_n] = []
        grouped_channels[core_n].append((clean_n, logo, url, cat))

    # --- GRAB FROM REMOTE SOURCES ---
    for src_url in SOURCES:
        print(f"Fetching from: {src_url}")
        try:
            resp = requests.get(src_url, timeout=15)
            resp.raise_for_status()
            parsed = parse_json(resp.text) if src_url.endswith('.json') else parse_m3u(resp.text)
            
            for name, logo, url, _ in parsed:
                url = url.strip()
                if not url.startswith("http") or url in seen_urls: continue
                
                cat = get_category(name)
                if not cat: continue 
                
                if cat == "Tamil Local Channels" and src_url not in LOCAL_SOURCES:
                    continue
                
                seen_urls.add(url)
                clean_n = clean_name(name)
                core_n = get_core_name(name)
                
                if core_n not in grouped_channels:
                    grouped_channels[core_n] = []
                grouped_channels[core_n].append((clean_n, logo, url, cat))
                
        except Exception:
            pass

    print(f"\n-> Deep-Testing {len(grouped_channels)} Unique Channels for fake/broken links...")
    print("   (Exact duplicates merged, foreign languages purged. All channels rigorously tested.)\n")
    
    final_channels = {cat: [] for cat in CATEGORY_ORDER}
    total_added = 0
    
    # --- MULTITHREADED CHECKING ---
    # Slowed down max_workers slightly to prevent dropped network connections
    groups_to_check = list(grouped_channels.values())
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        results = executor.map(check_stream_group, groups_to_check)
        for res in results:
            if res:
                orig_name, logo, url, cat = res
                final_channels[cat].append((orig_name, logo, url))
                total_added += 1

    # ==========================================
    # 6. SORTING A-Z & FILE GENERATION
    # ==========================================
    print("\nWriting perfectly ordered master_playlist.m3u...")
    with open("master_playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("#PLAYLIST:Checked by CODECS.COM M3U Checker\n")
        
        for cat in CATEGORY_ORDER:
            channels = final_channels.get(cat, [])
            if channels:
                channels.sort(key=lambda x: x[0].lower())
                f.write(f"\n# --- {cat} ---\n")
                for display_name, logo, url in channels:
                    f.write(f'#EXTINF:-1 tvg-name="{display_name}" tvg-logo="{logo}" group-title="{cat}",{display_name}\n{url}\n')

    print(f"\n✅ SUCCESS! Total Working Unique Channels: {total_added}")
    
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("# Tamil & English IPTV Playlist\n\n")
        f.write("This playlist is automatically checked, perfectly ordered, deduplicated, and updated every 6 hours.\n\n")
        f.write(f"**Total LIVE Channels:** {total_added}\n**Last Updated:** {timestamp}\n\n")
        f.write("## 📥 Playlist URL\n")
        f.write("Copy the link below and paste it directly into your IPTV Player:\n\n")
        f.write("`https://raw.githubusercontent.com/nuttle-nuttterr/Mk-tholaikaatchi-test/main/master_playlist.m3u`\n\n")
        f.write("## 📊 Channel Breakdown\n| Category | Count |\n|---|---|\n")
        
        for cat in CATEGORY_ORDER:
            channels = final_channels.get(cat, [])
            if channels:
                f.write(f"| {cat} | {len(channels)} |\n")

if __name__ == "__main__":
    main()
