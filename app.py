import os
import sys
import time
import json
import ssl
import re
import socket
import urllib.request
import urllib.parse
import urllib.error
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, 'static')

app = Flask(__name__, static_folder=static_dir, static_url_path='')
CORS(app)

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# =========================================================================
# CONFIGURATION
# =========================================================================
UPSTREAM_BASE_URL = "https://manoda.co"
CHANNEL = "pikaofficialnew"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

HEADERS = {
    "User-Agent": "Pikashow/2607211 (Android 14; Pixel 8 Pro; Channel/pikaofficialnew; gaid/96813245-1234-4567-8901-123456789012); Uuid/c8f29402849104",
    "Accept": "application/json"
}

LIVE_CACHE = {}

def sanitize_url(u):
    if not u:
        return ""
    try:
        parts = urllib.parse.urlsplit(u.strip())
        path = urllib.parse.quote(parts.path)
        query = urllib.parse.quote(parts.query, safe="=&?/:")
        return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))
    except Exception:
        return u.strip().replace(' ', '%20')

def filter_and_prioritize_servers(raw_urls):
    if not raw_urls:
        return []

    valid = []
    for s in raw_urls:
        u = sanitize_url(s.get('url', ''))
        if not u or 'slast430did' in u:
            continue
        valid.append({
            "label": s.get('label', 'Live Server'),
            "url": u
        })

    if not valid and raw_urls:
        valid = [{"label": s.get('label', 'Server'), "url": sanitize_url(s.get('url', ''))} for s in raw_urls if s.get('url')]

    def score(item):
        u = item.get('url', '').lower()
        if 'missipmain' in u or 'm3u8' in u:
            return 0
        if '.mp4' in u:
            return 1
        return 5

    valid.sort(key=score)

    cleaned = []
    for idx, s in enumerate(valid):
        lbl = f"Server {idx + 1} (High-Speed HD)" if idx == 0 else f"Server {idx + 1}"
        cleaned.append({
            "label": lbl,
            "url": s['url']
        })

    return cleaned

def upgrade_poster_quality(url):
    if not url:
        return ""
    if "image.tmdb.org/t/p/" in url:
        url = re.sub(r'/t/p/w\d+/', '/t/p/original/', url)
    if "media-amazon.com/images/" in url:
        if "@." in url:
            parts = url.split("@.")
            ext = "jpg"
            if url.endswith('.png'):
                ext = "png"
            elif url.endswith('.webp'):
                ext = "webp"
            return parts[0] + "@." + ext
    return url

def fetch_live_catalog(category):
    if category in LIVE_CACHE and (time.time() - LIVE_CACHE[category]['time'] < 86400):
        return LIVE_CACHE[category]['data']

    url = f"{UPSTREAM_BASE_URL}/v1/api/videos?type={category}&channel={CHANNEL}"
    print(f"[*] [LIVE API FETCH] Requesting {url}...")

    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
        data = resp.read().decode('utf-8')
        js = json.loads(data)
        raw_records = js.get('records', [])
        
        formatted = []
        for idx, r in enumerate(raw_records):
            raw_client_urls = r.get('clientUrls', [])
            if not raw_client_urls and r.get('url'):
                raw_client_urls = [{"label": "Server 1", "url": r.get('url')}]

            client_urls = filter_and_prioritize_servers(raw_client_urls)
            stream_url = client_urls[0]['url'] if client_urls else sanitize_url(r.get('url'))

            poster = r.get('c', '')
            if not poster or not poster.startswith('http'):
                poster = 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1200&auto=format&fit=crop&q=90'
            else:
                poster = upgrade_poster_quality(poster)

            formatted.append({
                "id": str(r.get('so', idx)),
                "title": r.get('t', 'Unknown Title'),
                "year": r.get('y', 2024),
                "genre": r.get('g', 'Movie'),
                "quality": r.get('q', '4K / 1080p HD'),
                "rating": "HD",
                "poster": poster,
                "stream_url": stream_url or "",
                "client_urls": client_urls,
                "languages": [
                    {"code": "hi", "name": "Hindi (Dolby Audio 5.1)"},
                    {"code": "en", "name": "English (Original Audio)"},
                    {"code": "ta", "name": "Tamil (Dubbed / Original)"},
                    {"code": "te", "name": "Telugu (Dubbed / Original)"},
                    {"code": "ml", "name": "Malayalam"},
                    {"code": "kn", "name": "Kannada"},
                    {"code": "pa", "name": "Punjabi"},
                    {"code": "bn", "name": "Bengali"}
                ]
            })

        # REVERSE ORDER: Recent/Latest on Page 1
        formatted.reverse()

        LIVE_CACHE[category] = {
            'time': time.time(),
            'data': formatted
        }
        print(f"[+] [SUCCESS] Fetched, Filtered & Reversed {len(formatted)} live titles for {category}")
        return formatted

@app.route('/')
def serve_index():
    return send_from_directory(static_dir, 'index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "online",
        "app_name": "LX-Player",
        "local_ip": LOCAL_IP,
        "local_url": f"http://127.0.0.1:5100",
        "network_url": f"http://{LOCAL_IP}:5100",
        "reversed_order": True,
        "hls_optimized": True
    })

# 100% LIVE CATALOG WITH REVERSED PAGINATION & SEARCH
@app.route('/api/videos', methods=['GET'])
@app.route('/v1/api/videos', methods=['GET'])
def get_videos():
    cat = request.args.get('type', 'bollywood').lower()
    search_q = request.args.get('search', '').strip().lower()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 30))

    try:
        if cat not in ['bollywood', 'hollywood', 'webseries', 'kdrama']:
            cat = 'bollywood'

        if cat == 'webseries':
            base_items = fetch_live_catalog('bollywood') + fetch_live_catalog('hollywood')
            keywords = ['season', 'episode', 'series', 's01', 's02', 's03', 'complete', 'show', 'pack', 'mirzapur', 'tv']
            exact = [it for it in base_items if any(kw in it['title'].lower() for kw in keywords)]
            additional = [it for it in base_items if any(g in it['genre'].lower() for g in ['sci-fi', 'mystery', 'thriller']) and it not in exact]
            items = exact + additional
        elif cat == 'kdrama':
            base_items = fetch_live_catalog('bollywood') + fetch_live_catalog('hollywood')
            keywords = ['korean', 'kdrama', 'k-drama', 'japan', 'chinese', 'asian']
            exact = [it for it in base_items if any(kw in it['title'].lower() or kw in it['genre'].lower() for kw in keywords)]
            additional = [it for it in base_items if any(g in it['genre'].lower() for g in ['romance', 'love']) and it not in exact]
            items = exact + additional
        else:
            items = fetch_live_catalog(cat)

        if search_q:
            filtered = [it for it in items if search_q in it['title'].lower() or search_q in it['genre'].lower() or search_q in str(it['year'])]
            total_items = len(filtered)
            total_pages = max(1, (total_items + limit - 1) // limit)
            start = (page - 1) * limit
            end = start + limit
            return jsonify({
                "code": 200,
                "status": "success",
                "total_available": total_items,
                "total_pages": total_pages,
                "page": page,
                "limit": limit,
                "records": filtered[start:end]
            })

        total_items = len(items)
        total_pages = max(1, (total_items + limit - 1) // limit)
        start = (page - 1) * limit
        end = start + limit
        paginated = items[start:end]

        return jsonify({
            "code": 200,
            "status": "success",
            "category": cat,
            "total_available": total_items,
            "total_pages": total_pages,
            "page": page,
            "limit": limit,
            "records": paginated
        })

    except Exception as e:
        return jsonify({
            "code": 500,
            "status": "error",
            "message": f"Fetch Error: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5100))
    print(f"===========================================================")
    print(f"  LX-Player - Ultra Streaming Engine")
    print(f"  > Local Access:   http://127.0.0.1:{port}")
    print(f"  > Network Access: http://{LOCAL_IP}:{port}")
    print(f"===========================================================")
    
    # Preload database catalog in background for instant first-page loads
    import threading
    def preload_catalog():
        print("[*] [PRELOAD] Starting background catalog preloading...")
        categories = ['bollywood', 'hollywood', 'webseries', 'kdrama']
        for cat in categories:
            try:
                fetch_live_catalog(cat)
                print(f"[+] [PRELOAD] Category successfully cached: {cat}")
            except Exception as e:
                print(f"[-] [PRELOAD] Failed to cache category {cat}: {str(e)}")
    threading.Thread(target=preload_catalog, daemon=True).start()

    app.run(host='0.0.0.0', port=port, debug=False)
