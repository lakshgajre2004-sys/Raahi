from flask import Flask, render_template_string
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

SERVER_URL = 'http://localhost:8090'

ADMIN_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raahi Admin Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #000000;
            min-height: 100vh;
            color: #fff;
            overflow-x: hidden;
        }

        .bg-pattern {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.02) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.02) 0%, transparent 50%);
            animation: bgMove 20s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }

        @keyframes bgMove {
            0%, 100% { opacity: 0.5; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.1); }
        }

        .dashboard-header {
            position: relative;
            z-index: 1;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            padding: 30px 40px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .header-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .logo-section {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .admin-logo {
            font-size: 42px;
            font-weight: 800;
            background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.7) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .admin-badge {
            background: rgba(255, 255, 255, 0.15);
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            color: #fff;
        }

        .refresh-section {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .auto-refresh-toggle {
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(255, 255, 255, 0.08);
            padding: 10px 20px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .switch {
            position: relative;
            width: 50px;
            height: 26px;
        }

        .switch input { opacity: 0; width: 0; height: 0; }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: rgba(255, 255, 255, 0.2);
            transition: .4s;
            border-radius: 26px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 18px;
            width: 18px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }

        input:checked + .slider { background-color: #4cd964; }
        input:checked + .slider:before { transform: translateX(24px); }

        .refresh-btn {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 12px 24px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .refresh-btn:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
        }

        .stat-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
            padding: 24px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-4px);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .stat-icon {
            font-size: 32px;
            margin-bottom: 12px;
        }

        .stat-value {
            font-size: 36px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 8px;
        }

        .stat-label {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.6);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .dashboard-container {
            position: relative;
            z-index: 1;
            max-width: 1600px;
            margin: 0 auto;
            padding: 40px 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }

        .panel {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            padding: 30px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }

        .panel:hover {
            border-color: rgba(255, 255, 255, 0.2);
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .panel-title {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 20px;
            font-weight: 700;
        }

        .panel-icon {
            width: 40px;
            height: 40px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }

        .panel-count {
            background: rgba(255, 255, 255, 0.15);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 600;
        }

        .full-width {
            grid-column: 1 / -1;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        thead {
            background: rgba(255, 255, 255, 0.05);
        }

        th {
            padding: 14px;
            text-align: left;
            font-size: 12px;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.7);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        td {
            padding: 16px 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9);
        }

        tr:hover {
            background: rgba(255, 255, 255, 0.03);
        }

        .status-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .status-online {
            background: rgba(76, 217, 100, 0.2);
            color: #4cd964;
            border: 1px solid rgba(76, 217, 100, 0.3);
        }

        .status-offline {
            background: rgba(255, 59, 48, 0.2);
            color: #ff3b30;
            border: 1px solid rgba(255, 59, 48, 0.3);
        }

        .status-requested {
            background: rgba(255, 204, 0, 0.2);
            color: #ffcc00;
            border: 1px solid rgba(255, 204, 0, 0.3);
        }

        .status-accepted {
            background: rgba(90, 200, 250, 0.2);
            color: #5ac8fa;
            border: 1px solid rgba(90, 200, 250, 0.3);
        }

        .status-in_progress {
            background: rgba(76, 217, 100, 0.2);
            color: #4cd964;
            border: 1px solid rgba(76, 217, 100, 0.3);
        }

        .status-completed {
            background: rgba(255, 255, 255, 0.2);
            color: #fff;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .queue-position {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
            padding: 6px 12px;
            border-radius: 12px;
            font-weight: 700;
            color: #fff;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: rgba(255, 255, 255, 0.5);
        }

        .empty-icon {
            font-size: 64px;
            margin-bottom: 16px;
            opacity: 0.3;
        }

        .scrollable {
            max-height: 400px;
            overflow-y: auto;
        }

        .scrollable::-webkit-scrollbar {
            width: 8px;
        }

        .scrollable::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }

        .scrollable::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
        }

        .scrollable::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .live-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #4cd964;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s ease-in-out infinite;
        }

        @media (max-width: 1200px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .dashboard-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="bg-pattern"></div>

    <div class="dashboard-header">
        <div class="header-top">
            <div class="logo-section">
                <div class="admin-logo">🚗 RAAHI</div>
                <div class="admin-badge">⚡ ADMIN DASHBOARD</div>
            </div>
            <div class="refresh-section">
                <div class="auto-refresh-toggle">
                    <span style="font-size: 13px; color: rgba(255,255,255,0.7);">Auto-refresh</span>
                    <label class="switch">
                        <input type="checkbox" id="autoRefreshToggle" checked onchange="toggleAutoRefresh()">
                        <span class="slider"></span>
                    </label>
                </div>
                <button class="refresh-btn" onclick="refreshAll()">
                    🔄 Refresh Now
                </button>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-value" id="totalUsers">-</div>
                <div class="stat-label">Total Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">👨‍✈️</div>
                <div class="stat-value" id="totalDrivers">-</div>
                <div class="stat-label">Total Drivers</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🚗</div>
                <div class="stat-value" id="onlineDrivers">-</div>
                <div class="stat-label">Drivers Online</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🎯</div>
                <div class="stat-value" id="activeRides">-</div>
                <div class="stat-label">Active Rides</div>
            </div>
        </div>
    </div>

    <div class="dashboard-container">
        <!-- Ride Queue Panel -->
        <div class="panel full-width">
            <div class="panel-header">
                <div class="panel-title">
                    <div class="panel-icon">📋</div>
                    <span><span class="live-indicator"></span>Ride Request Queue</span>
                </div>
                <div class="panel-count" id="queueCount">0 in queue</div>
            </div>
            <div class="scrollable">
                <table>
                    <thead>
                        <tr>
                            <th>Queue #</th>
                            <th>Ride ID</th>
                            <th>User ID</th>
                            <th>From</th>
                            <th>To</th>
                            <th>Fare</th>
                            <th>Status</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody id="queueTable">
                        <tr>
                            <td colspan="8">
                                <div class="empty-state">
                                    <div class="empty-icon">📋</div>
                                    <p>No rides in queue</p>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Registered Users Panel -->
        <div class="panel">
            <div class="panel-header">
                <div class="panel-title">
                    <div class="panel-icon">👥</div>
                    <span>Registered Users</span>
                </div>
                <div class="panel-count" id="usersCount">0</div>
            </div>
            <div class="scrollable">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Phone</th>
                        </tr>
                    </thead>
                    <tbody id="usersTable">
                        <tr>
                            <td colspan="4">
                                <div class="empty-state">
                                    <div class="empty-icon">👥</div>
                                    <p>No users registered</p>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Registered Drivers Panel -->
        <div class="panel">
            <div class="panel-header">
                <div class="panel-title">
                    <div class="panel-icon">👨‍✈️</div>
                    <span>Registered Drivers</span>
                </div>
                <div class="panel-count" id="driversCount">0</div>
            </div>
            <div class="scrollable">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Vehicle</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="driversTable">
                        <tr>
                            <td colspan="4">
                                <div class="empty-state">
                                    <div class="empty-icon">👨‍✈️</div>
                                    <p>No drivers registered</p>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Active Rides Panel -->
        <div class="panel full-width">
            <div class="panel-header">
                <div class="panel-title">
                    <div class="panel-icon">🚕</div>
                    <span><span class="live-indicator"></span>Active & Recent Rides</span>
                </div>
                <div class="panel-count" id="ridesCount">0 rides</div>
            </div>
            <div class="scrollable">
                <table>
                    <thead>
                        <tr>
                            <th>Ride ID</th>
                            <th>User</th>
                            <th>Driver</th>
                            <th>From</th>
                            <th>To</th>
                            <th>Fare</th>
                            <th>Status</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody id="ridesTable">
                        <tr>
                            <td colspan="8">
                                <div class="empty-state">
                                    <div class="empty-icon">🚕</div>
                                    <p>No rides yet</p>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const SERVER_URL = 'http://localhost:8090';
        let autoRefreshInterval = null;

        function toggleAutoRefresh() {
            const toggle = document.getElementById('autoRefreshToggle');
            if (toggle.checked) {
                startAutoRefresh();
            } else {
                stopAutoRefresh();
            }
        }

        function startAutoRefresh() {
            if (autoRefreshInterval) return;
            console.log('📡 Auto-refresh started');
            refreshAll();
            autoRefreshInterval = setInterval(() => {
                refreshAll();
            }, 2000); // Refresh every 2 seconds
        }

        function stopAutoRefresh() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
                console.log('⏸️ Auto-refresh stopped');
            }
        }

        async function refreshAll() {
            await Promise.all([
                loadUsers(),
                loadDrivers(),
                loadRides(),
                loadQueue()
            ]);
            updateStats();
        }

        async function loadUsers() {
            try {
                const response = await fetch(`${SERVER_URL}/api/admin/users`);
                const data = await response.json();

                if (data.success && data.data) {
                    const tbody = document.getElementById('usersTable');
                    if (data.data.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="4"><div class="empty-state"><div class="empty-icon">👥</div><p>No users</p></div></td></tr>';
                    } else {
                        tbody.innerHTML = data.data.map(user => `
                            <tr>
                                <td><strong>#${user.id}</strong></td>
                                <td>${user.name}</td>
                                <td>${user.email}</td>
                                <td>${user.phone || 'N/A'}</td>
                            </tr>
                        `).join('');
                    }
                    document.getElementById('usersCount').textContent = data.data.length;
                }
            } catch (error) {
                console.error('Error loading users:', error);
            }
        }

        async function loadDrivers() {
            try {
                const response = await fetch(`${SERVER_URL}/api/admin/drivers`);
                const data = await response.json();

                if (data.success && data.data) {
                    const tbody = document.getElementById('driversTable');
                    if (data.data.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="4"><div class="empty-state"><div class="empty-icon">👨‍✈️</div><p>No drivers</p></div></td></tr>';
                    } else {
                        tbody.innerHTML = data.data.map(driver => `
                            <tr>
                                <td><strong>#${driver.id}</strong></td>
                                <td>${driver.name}</td>
                                <td>${driver.vehicle_details || 'N/A'}</td>
                                <td><span class="status-badge status-${driver.online_status}">${driver.online_status}</span></td>
                            </tr>
                        `).join('');
                    }
                    document.getElementById('driversCount').textContent = data.data.length;
                }
            } catch (error) {
                console.error('Error loading drivers:', error);
            }
        }

        async function loadRides() {
            try {
                const response = await fetch(`${SERVER_URL}/api/admin/rides`);
                const data = await response.json();

                if (data.success && data.data) {
                    const tbody = document.getElementById('ridesTable');
                    if (data.data.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="8"><div class="empty-state"><div class="empty-icon">🚕</div><p>No rides</p></div></td></tr>';
                    } else {
                        tbody.innerHTML = data.data.map(ride => `
                            <tr>
                                <td><strong>#${ride.id}</strong></td>
                                <td>User #${ride.user_id}</td>
                                <td>${ride.driver_id ? 'Driver #' + ride.driver_id : '-'}</td>
                                <td>${ride.source_location}</td>
                                <td>${ride.dest_location}</td>
                                <td><strong>₹${ride.fare}</strong></td>
                                <td><span class="status-badge status-${ride.status}">${ride.status.replace('_', ' ')}</span></td>
                                <td>${formatTime(ride.created_at)}</td>
                            </tr>
                        `).join('');
                    }
                    document.getElementById('ridesCount').textContent = `${data.data.length} rides`;
                }
            } catch (error) {
                console.error('Error loading rides:', error);
            }
        }

        async function loadQueue() {
            try {
                const response = await fetch(`${SERVER_URL}/api/rides/available`);
                const data = await response.json();

                if (data.success && data.data) {
                    const tbody = document.getElementById('queueTable');
                    if (data.data.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="8"><div class="empty-state"><div class="empty-icon">📋</div><p>No rides in queue</p></div></td></tr>';
                    } else {
                        tbody.innerHTML = data.data.map((ride, index) => `
                            <tr>
                                <td><span class="queue-position">#${index + 1}</span></td>
                                <td><strong>#${ride.id}</strong></td>
                                <td>User #${ride.user_id}</td>
                                <td>${ride.source_location}</td>
                                <td>${ride.dest_location}</td>
                                <td><strong>₹${ride.fare}</strong></td>
                                <td><span class="status-badge status-requested">In Queue</span></td>
                                <td>${formatTime(ride.created_at)}</td>
                            </tr>
                        `).join('');
                    }
                    document.getElementById('queueCount').textContent = `${data.data.length} in queue`;
                }
            } catch (error) {
                console.error('Error loading queue:', error);
            }
        }

        async function updateStats() {
            try {
                const response = await fetch(`${SERVER_URL}/api/admin/stats`);
                const data = await response.json();

                if (data.success && data.stats) {
                    document.getElementById('totalUsers').textContent = data.stats.total_users;
                    document.getElementById('totalDrivers').textContent = data.stats.total_drivers;
                    document.getElementById('onlineDrivers').textContent = data.stats.online_drivers;
                    document.getElementById('activeRides').textContent = data.stats.active_rides;
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        function formatTime(timestamp) {
            if (!timestamp) return 'N/A';
            const date = new Date(timestamp);
            const now = new Date();
            const diff = Math.floor((now - date) / 1000);

            if (diff < 60) return `${diff}s ago`;
            if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
            if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
            return date.toLocaleDateString();
        }

        // Initialize
        startAutoRefresh();
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(ADMIN_DASHBOARD_HTML)

if __name__ == '__main__':
    print('=' * 70)
    print('⚡ Raahi Admin Dashboard')
    print('=' * 70)
    print('Dashboard running at: http://localhost:9000')
    print('Auto-refresh: Every 2 seconds')
    print('Server connection: http://localhost:8090')
    print('=' * 70)
    app.run(host='0.0.0.0', port=9000, debug=True, use_reloader=False)