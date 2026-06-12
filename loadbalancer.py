from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import threading
import time
from collections import defaultdict

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

        # Rotate after configured number of requests
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
            except Exception:
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

        # Return proxied response unchanged (clean)
        return resp.content, resp.status_code, dict(resp.headers)

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


# ============================
# RUN SERVER
# ============================
if __name__ == "__main__":
    print("=" * 70)
    print("⚡ CLEAN LOAD BALANCER (Every {} Requests)".format(MAX_REQUESTS_PER_SERVER))
    print("=" * 70)
    print("Running on http://localhost:8090")
    print("Backends:")
    for s in BACKEND_SERVERS:
        print("  -", s)
    print("=" * 70)

    app.run(host="0.0.0.0", port=8090, debug=False, threaded=True)
