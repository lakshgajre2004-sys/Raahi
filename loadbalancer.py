from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import threading
import time
from collections import defaultdict
import json

app = Flask(__name__)
CORS(app)

# ============================
# CONFIGURATION
# ============================
BACKEND_SERVERS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://localhost:3002',
]

MAX_REQUESTS_PER_SERVER = 4

request_counts = defaultdict(int)
server_health = {s: True for s in BACKEND_SERVERS}
current_server_index = 0
total_requests = 0

lock = threading.Lock()


# ============================
# LOAD BALANCER CORE
# ============================
def get_next_server():
    global current_server_index, total_requests

    with lock:
        backend = BACKEND_SERVERS[current_server_index]

        # Rotate after 4 requests
        if request_counts[backend] >= MAX_REQUESTS_PER_SERVER:
            request_counts[backend] = 0
            current_server_index = (current_server_index + 1) % len(BACKEND_SERVERS)
            backend = BACKEND_SERVERS[current_server_index]

        request_counts[backend] += 1
        total_requests += 1

        return backend


# ============================
# BACKGROUND HEALTH CHECK
# ============================
def check_health():
    while True:
        for server in BACKEND_SERVERS:
            try:
                r = requests.get(f"{server}/api/health", timeout=2)
                server_health[server] = r.status_code == 200
            except:
                server_health[server] = False
        time.sleep(5)


threading.Thread(target=check_health, daemon=True).start()


# ============================
# UNIVERSAL PROXY ENDPOINT
# ============================
@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy(path):
    backend = get_next_server()
    url = f"{backend}/{path}"

    try:
        if request.method == "GET":
            resp = requests.get(url, params=request.args, timeout=30)
        else:
            resp = requests.request(
                request.method,
                url,
                json=request.get_json(silent=True),
                timeout=30,
            )

        # Build response headers
        headers = dict(resp.headers)
        headers["X-Backend-Server"] = backend

        # Default body
        body = resp.content

        # If JSON, add served_by
        if "application/json" in resp.headers.get("Content-Type", "").lower():
            try:
                parsed = resp.json()
                if isinstance(parsed, dict):
                    parsed["served_by"] = backend
                    body = json.dumps(parsed).encode("utf-8")
                    headers["Content-Length"] = str(len(body))
            except:
                pass

        return body, resp.status_code, headers

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Backend unreachable",
            "details": str(e)
        }), 503


# ============================
# LB INTERNAL STATUS
# ============================
@app.route("/lb/status")
def lb_status():
    return jsonify({
        "load_balancer": "running",
        "current_server": BACKEND_SERVERS[current_server_index],
        "total_requests": total_requests,
        "switch_threshold": MAX_REQUESTS_PER_SERVER,
        "servers": [
            {
                "url": s,
                "healthy": server_health[s],
                "request_count": request_counts[s],
                "is_current": s == BACKEND_SERVERS[current_server_index]
            }
            for s in BACKEND_SERVERS
        ]
    })

# Debug helper: reset LB counters without restarting (POST /lb/reset)
@app.route('/lb/reset', methods=['POST'])
def lb_reset():
    global request_counts, current_server_index, total_requests
    with lock:
        request_counts = defaultdict(int)
        current_server_index = 0
        total_requests = 0
    return jsonify({'success': True, 'message': 'load balancer counters reset'}), 200



# ============================
# RUN SERVER
# ============================
if __name__ == "__main__":
    print("=" * 70)
    print("⚡ FIXED LOAD BALANCER (Every 4 Requests)")
    print("=" * 70)
    print("Running on http://localhost:8090")
    print("Backends:")
    for s in BACKEND_SERVERS:
        print("  -", s)
    print("=" * 70)

    app.run(host="0.0.0.0", port=8090, debug=False, threaded=True)
