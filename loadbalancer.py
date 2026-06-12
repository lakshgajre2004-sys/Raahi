from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import threading
import time
from collections import defaultdict

app = Flask(__name__)
CORS(app)

# Configuration
BACKEND_SERVERS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://localhost:3002',
]

# Track request count per server
request_counts = defaultdict(int)
server_health = {server: True for server in BACKEND_SERVERS}
current_server_index = 0
total_requests = 0
lock = threading.Lock()

# Switch server after every 4 requests
MAX_REQUESTS_PER_SERVER = 4

def get_next_server():
    """Round-robin load balancing - switches after every 4 requests"""
    global current_server_index, total_requests

    with lock:
        current_server = BACKEND_SERVERS[current_server_index]

        if request_counts[current_server] >= MAX_REQUESTS_PER_SERVER:
            old_server = current_server
            request_counts[current_server] = 0
            current_server_index = (current_server_index + 1) % len(BACKEND_SERVERS)
            current_server = BACKEND_SERVERS[current_server_index]
            print(f"🔄 SWITCHING: {old_server} → {current_server} (after {MAX_REQUESTS_PER_SERVER} requests)")

        attempts = 0
        while not server_health.get(current_server, False) and attempts < len(BACKEND_SERVERS):
            print(f"⚠️ {current_server} is unhealthy, trying next server...")
            current_server_index = (current_server_index + 1) % len(BACKEND_SERVERS)
            current_server = BACKEND_SERVERS[current_server_index]
            attempts += 1

        request_counts[current_server] += 1
        total_requests += 1

        return current_server


def check_server_health():
    """Background thread to check server health"""
    while True:
        for server in BACKEND_SERVERS:
            try:
                response = requests.get(f'{server}/api/health', timeout=2)
                was_down = not server_health.get(server, True)
                server_health[server] = response.status_code == 200

                if was_down and server_health[server]:
                    print(f"✅ {server} is back ONLINE")
                elif not server_health[server]:
                    print(f"❌ {server} is DOWN")

            except Exception as e:
                if server_health.get(server, True):
                    print(f"❌ {server} is UNREACHABLE: {str(e)}")
                server_health[server] = False

        time.sleep(5)

# Start health check thread
health_thread = threading.Thread(target=check_server_health, daemon=True)
health_thread.start()


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    """Proxy all requests to backend servers with load balancing"""
    backend_server = get_next_server()
    url = f'{backend_server}/{path}'

    try:
        if request.method == 'GET':
            response = requests.get(url, params=request.args, timeout=30)
        elif request.method == 'POST':
            response = requests.post(url, json=request.get_json(), timeout=30)
        elif request.method == 'PUT':
            response = requests.put(url, json=request.get_json(), timeout=30)
        elif request.method == 'DELETE':
            response = requests.delete(url, timeout=30)
        else:
            response = requests.request(request.method, url, json=request.get_json(), timeout=30)

        req_num = request_counts[backend_server]
        print(f"✅ Request #{total_requests}: {request.method} /{path} → {backend_server} [{req_num}/{MAX_REQUESTS_PER_SERVER}]")

        return response.content, response.status_code, dict(response.headers)

    except requests.exceptions.RequestException as e:
        print(f"❌ Error forwarding to {backend_server}: {e}")
        server_health[backend_server] = False
        return jsonify({'success': False, 'error': 'Backend server unavailable'}), 503


@app.route('/lb/status', methods=['GET'])
def load_balancer_status():
    return jsonify({
        'load_balancer': 'running',
        'current_server': BACKEND_SERVERS[current_server_index],
        'servers': [
            {
                'url': server,
                'healthy': server_health[server],
                'request_count': request_counts[server],
                'is_current': server == BACKEND_SERVERS[current_server_index]
            }
            for server in BACKEND_SERVERS
        ],
        'total_requests': total_requests,
        'switch_threshold': MAX_REQUESTS_PER_SERVER
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    healthy_servers = sum(1 for status in server_health.values() if status)
    return jsonify({
        'load_balancer': 'healthy',
        'backend_servers': len(BACKEND_SERVERS),
        'healthy_servers': healthy_servers,
        'total_requests': total_requests
    })


if __name__ == '__main__':
    print('=' * 70)
    print('⚡ RAAHI LOAD BALANCER (Every 4 Requests)')
    print('=' * 70)
    print('Load Balancer Port: 8090')  # Updated
    print('Backend Servers:')
    for i, server in enumerate(BACKEND_SERVERS, 1):
        print(f'  {i}. {server}')
    print(f'\n📊 Strategy: Switch server every {MAX_REQUESTS_PER_SERVER} requests')
    print('=' * 70)
    print('🔍 Status: http://localhost:8090/lb/status')  # Updated
    print('=' * 70)
    app.run(host='0.0.0.0', port=8090, debug=False, threaded=True)
