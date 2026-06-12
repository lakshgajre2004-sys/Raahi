from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import sys

app = Flask(__name__)
CORS(app)

SERVER_URL = 'http://localhost:3000'

USER_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .auth-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
            max-width: 900px;
            width: 100%;
            display: flex;
            min-height: 500px;
        }
        .auth-sidebar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            flex: 1;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .auth-sidebar h1 { font-size: 32px; margin-bottom: 20px; }
        .auth-sidebar p { opacity: 0.9; line-height: 1.6; }
        .auth-content {
            flex: 1.5;
            padding: 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .auth-tabs {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            border-bottom: 2px solid #eee;
        }
        .auth-tab {
            padding: 10px 20px;
            background: none;
            border: none;
            color: #999;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .auth-tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        .auth-form { display: none; }
        .auth-form.active { display: block; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .form-group { margin-bottom: 20px; }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 15px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:active { transform: translateY(0); }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        /* Dashboard Styles */
        .dashboard-container {
            background: #f5f7fa;
            min-height: 100vh;
            padding: 20px;
        }
        .dashboard-header {
            background: white;
            padding: 20px 30px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .dashboard-header h2 { color: #667eea; margin: 0; }
        .logout-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .panel {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .panel h3 {
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        .alert {
            padding: 12px 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            display: none;
        }
        .alert.success {
            background: #d4edda;
            color: #155724;
            border-left: 4px solid #28a745;
        }
        .alert.error {
            background: #f8d7da;
            color: #721c24;
            border-left: 4px solid #dc3545;
        }
        .alert.show { display: block; animation: slideIn 0.3s; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        
        .location-input {
            position: relative;
            margin-bottom: 20px;
        }
        .location-icon {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #667eea;
        }
        .location-input input {
            padding-left: 45px;
        }
        .queue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-top: 15px;
        }
        .queue-card .position {
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }
        .queue-card .label {
            text-align: center;
            opacity: 0.9;
            font-size: 16px;
        }
        .queue-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }
        .queue-stat {
            background: rgba(255,255,255,0.2);
            padding: 10px;
            border-radius: 6px;
            text-align: center;
        }
        .queue-stat .number {
            font-size: 24px;
            font-weight: bold;
        }
        .queue-stat .text {
            font-size: 12px;
            opacity: 0.9;
        }
        .queue-note {
            background: rgba(255,255,255,0.15);
            padding: 10px;
            border-radius: 6px;
            margin-top: 10px;
            font-size: 13px;
            text-align: center;
        }
        .ride-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        .ride-card p { margin: 8px 0; }
        .ride-card .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .status.requested { background: #fff3cd; color: #856404; }
        .status.accepted { background: #d1ecf1; color: #0c5460; }
        .status.in_progress { background: #d4edda; color: #155724; }
        .status.completed { background: #d6d8db; color: #383d41; }
        
        /* Pulse animation for position changes */
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        .position-updated {
            animation: pulse 0.5s ease-in-out;
        }
        
        @media (max-width: 768px) {
            .auth-container { flex-direction: column; }
            .auth-sidebar { padding: 30px; }
            .dashboard-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <!-- Authentication View -->
    <div id="auth-view" class="auth-container">
        <div class="auth-sidebar">
            <h1>Mini Uber</h1>
            <p>Book rides instantly with our easy-to-use platform. Get real-time fare estimates, track your queue position, and enjoy a seamless transportation experience.</p>
        </div>
        <div class="auth-content">
            <div class="auth-tabs">
                <button class="auth-tab active" onclick="switchTab('register')">Register</button>
                <button class="auth-tab" onclick="switchTab('login')">Login</button>
            </div>
            
            <form id="register-form" class="auth-form active" onsubmit="registerUser(event)">
                <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" id="regName" placeholder="Enter your full name" required>
                </div>
                <div class="form-group">
                    <label>Email Address</label>
                    <input type="email" id="regEmail" placeholder="Enter your email" required>
                </div>
                <div class="form-group">
                    <label>Phone Number</label>
                    <input type="tel" id="regPhone" placeholder="Enter your phone number" required>
                </div>
                <button type="submit" class="btn" id="registerBtn">Create Account</button>
            </form>
            
            <form id="login-form" class="auth-form" onsubmit="login(event)">
                <div class="form-group">
                    <label>User ID</label>
                    <input type="number" id="loginUserId" placeholder="Enter your user ID" required>
                </div>
                <button type="submit" class="btn">Login to Dashboard</button>
            </form>
        </div>
    </div>

    <!-- Dashboard View -->
    <div id="dashboard-view" class="dashboard-container" style="display: none;">
        <div class="dashboard-header">
            <h2 id="welcome-message">Welcome!</h2>
            <button class="logout-btn" onclick="logout()">Logout</button>
        </div>
        
        <div class="dashboard-grid">
            <div class="panel">
                <h3>Request a Ride</h3>
                <div id="rideAlert" class="alert"></div>
                
                <form onsubmit="requestRide(event)">
                    <div class="location-input">
                        <span class="location-icon">📍</span>
                        <input type="text" id="source" placeholder="Pickup location" required>
                    </div>
                    
                    <div class="location-input">
                        <span class="location-icon">🎯</span>
                        <input type="text" id="destination" placeholder="Drop-off location" required>
                    </div>
                    
                    <button type="submit" class="btn" id="rideBtn">Request Ride</button>
                </form>
                
                <div id="queueDisplay" style="display: none;"></div>
            </div>
            
            <div class="panel">
                <h3>My Rides</h3>
                <button onclick="loadMyRides()" class="btn" style="margin-bottom: 15px;">Refresh Rides</button>
                <div id="myRides">Click refresh to load your rides</div>
            </div>
        </div>
    </div>

    <script>
        let currentUserId = null;
        let queueCheckInterval = null;
        let currentRideId = null;
        let lastQueuePosition = null;

        function switchTab(tab) {
            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            
            if (tab === 'register') {
                document.querySelectorAll('.auth-tab')[0].classList.add('active');
                document.getElementById('register-form').classList.add('active');
            } else {
                document.querySelectorAll('.auth-tab')[1].classList.add('active');
                document.getElementById('login-form').classList.add('active');
            }
        }

        function showAlert(message, type = 'success') {
            const alert = document.getElementById('rideAlert');
            alert.textContent = message;
            alert.className = `alert ${type} show`;
            setTimeout(() => alert.classList.remove('show'), 5000);
        }

        async function registerUser(e) {
            e.preventDefault();
            const name = document.getElementById('regName').value.trim();
            const email = document.getElementById('regEmail').value.trim();
            const phone = document.getElementById('regPhone').value.trim();

            const registerBtn = document.getElementById('registerBtn');
            registerBtn.disabled = true;
            registerBtn.textContent = 'Creating Account...';

            try {
                const response = await fetch('/api/user/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, phone })
                });

                const result = await response.json();
                
                if (!response.ok) {
                    throw new Error(result.error || result.details || 'Registration failed');
                }

                alert(`Registration successful! Your User ID is ${result.user_id}`);
                switchTab('login');
                document.getElementById('loginUserId').value = result.user_id;
                document.getElementById('regName').value = '';
                document.getElementById('regEmail').value = '';
                document.getElementById('regPhone').value = '';

            } catch (error) {
                alert(`Registration Error: ${error.message}`);
            } finally {
                registerBtn.disabled = false;
                registerBtn.textContent = 'Create Account';
            }
        }

        async function login(e) {
            e.preventDefault();
            const userId = document.getElementById('loginUserId').value;
            
            currentUserId = userId;
            document.getElementById('auth-view').style.display = 'none';
            document.getElementById('dashboard-view').style.display = 'block';
            document.getElementById('welcome-message').textContent = `Welcome, User ${userId}!`;
            
            // Load rides on login and check for active queued rides
            await loadMyRides();
            await checkForQueuedRides();
        }

        function logout() {
            if (queueCheckInterval) {
                clearInterval(queueCheckInterval);
            }
            currentUserId = null;
            currentRideId = null;
            lastQueuePosition = null;
            document.getElementById('auth-view').style.display = 'flex';
            document.getElementById('dashboard-view').style.display = 'none';
            document.getElementById('loginUserId').value = '';
            document.getElementById('source').value = '';
            document.getElementById('destination').value = '';
            document.getElementById('queueDisplay').style.display = 'none';
        }

        async function requestRide(e) {
            e.preventDefault();
            const source = document.getElementById('source').value.trim();
            const destination = document.getElementById('destination').value.trim();

            const rideBtn = document.getElementById('rideBtn');
            rideBtn.disabled = true;
            rideBtn.textContent = 'Requesting Ride...';

            try {
                const response = await fetch('/api/user/request-ride-queue', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: parseInt(currentUserId),
                        source_location: source,
                        dest_location: destination
                    })
                });

                const result = await response.json();
                
                if (!response.ok) {
                    throw new Error(result.error || result.details || 'Ride request failed');
                }

                showAlert(`Ride requested successfully! Ride ID: ${result.ride_id}`, 'success');
                
                // Store current ride ID for queue tracking
                currentRideId = result.ride_id;
                lastQueuePosition = result.queue_position;
                
                // Display queue information
                displayQueueInfo(result);
                
                // Start checking queue position
                startQueueCheck(result.ride_id);
                
                document.getElementById('source').value = '';
                document.getElementById('destination').value = '';
                
                // Refresh rides list
                loadMyRides();

            } catch (error) {
                showAlert(`Ride Request Error: ${error.message}`, 'error');
            } finally {
                rideBtn.disabled = false;
                rideBtn.textContent = 'Request Ride';
            }
        }

        function displayQueueInfo(data) {
            const queueDisplay = document.getElementById('queueDisplay');
            queueDisplay.innerHTML = `
                <div class="queue-card">
                    <div class="position" id="queuePosition">#${data.queue_position}</div>
                    <div class="label">Your Position in Queue</div>
                    <div class="queue-info">
                        <div class="queue-stat">
                            <div class="number" id="onlineDrivers">${data.online_drivers || 0}</div>
                            <div class="text">Drivers Online</div>
                        </div>
                        <div class="queue-stat">
                            <div class="number" id="estimatedFare">₹${data.estimated_fare}</div>
                            <div class="text">Estimated Fare</div>
                        </div>
                    </div>
                    <div class="queue-note">
                        🔄 Auto-updating every second - Position updates when drivers accept rides
                    </div>
                </div>
            `;
            queueDisplay.style.display = 'block';
        }

        function updateQueueDisplay(data) {
            const positionElement = document.getElementById('queuePosition');
            const onlineDriversElement = document.getElementById('onlineDrivers');
            
            if (positionElement && onlineDriversElement) {
                // Check if position changed
                const newPosition = data.queue_position;
                const currentPosition = parseInt(positionElement.textContent.replace('#', ''));
                
                if (newPosition !== currentPosition) {
                    // Position changed - add animation
                    positionElement.classList.add('position-updated');
                    setTimeout(() => positionElement.classList.remove('position-updated'), 500);
                    
                    // Show notification if position improved
                    if (newPosition < currentPosition) {
                        showAlert(`Your queue position moved up to #${newPosition}!`, 'success');
                    }
                }
                
                positionElement.textContent = `#${newPosition}`;
                onlineDriversElement.textContent = data.online_drivers;
                
                // Update total waiting if element exists
                const totalWaitingElement = document.getElementById('totalWaiting');
                if (totalWaitingElement) {
                    totalWaitingElement.textContent = data.total_waiting;
                }
            }
        }

    function startQueueCheck(rideId) {
            // Always clear any previous interval to avoid multiple loops
            if (queueCheckInterval) clearInterval(queueCheckInterval);

            // Start new polling every 3 seconds
            queueCheckInterval = setInterval(async () => {
                try {
                    // --- FIX: Add cache-busting headers ---
                    const response = await fetch(`/api/user/queue-position/${rideId}`, {
                        method: 'GET',
                        cache: 'no-cache' // Most important fix
                    });

                    if (!response.ok) {
                        // If the server returns an error (like 404), stop polling
                        throw new Error(`Server returned status ${response.status}`);
                    }

                    const data = await response.json();

                    // --- FIX: Use correct property names from server (with underscores) ---
                    if (data.success && data.in_queue && data.status === 'requested') {
                        // Still in queue, update the display
                        updateQueueDisplay(data);
                        lastQueuePosition = data.queue_position;
                    } else {
                        // Ride has left the queue (accepted, completed, etc.)
                        clearInterval(queueCheckInterval);
                        queueCheckInterval = null;
                        currentRideId = null;
                        lastQueuePosition = null;
                        document.getElementById('queueDisplay').style.display = 'none';

                        // Show a specific alert based on the final status
                        if (data.status === 'accepted') {
                            showAlert('Your ride has been accepted by a driver!', 'success');
                        } else if (data.status === 'in_progress') {
                            showAlert('Your ride is in progress!', 'success');
                        }
                        
                        // --- FIX: Immediately refresh the ride list ---
                        loadMyRides();
                    }
                } catch (error) {
                    console.error('Error checking queue, stopping poll:', error);
                    clearInterval(queueCheckInterval); // Stop on error
                }
            }, 3000); // Poll every 3 seconds is more reasonable than 1 second
        }

        
        // Check for any existing queued rides when logging in
        async function checkForQueuedRides() {
            try {
                const response = await fetch(`/api/user/rides/${currentUserId}`);
                const data = await response.json();
                
                if (data.success && data.data) {
                    // Find the most recent requested ride
                    const requestedRide = data.data.find(ride => ride.status === 'requested');
                    
                    if (requestedRide) {
                        console.log('Found existing queued ride:', requestedRide.id);
                        currentRideId = requestedRide.id;
                        
                        // Get queue position for this ride
                        const queueResponse = await fetch(`/api/user/queue-position/${requestedRide.id}`);
                        const queueData = await queueResponse.json();
                        
                        if (queueData.success && queueData.in_queue) {
                            displayQueueInfo({
                                queue_position: queueData.queue_position,
                                online_drivers: queueData.online_drivers,
                                estimated_fare: requestedRide.fare
                            });
                            lastQueuePosition = queueData.queue_position;
                            startQueueCheck(requestedRide.id);
                            
                            showAlert('Resumed tracking your ride in queue', 'success');
                        }
                    }
                }
            } catch (error) {
                console.error('Error checking for queued rides:', error);
            }
        }

        async function loadMyRides() {
            const ridesDiv = document.getElementById('myRides');
            ridesDiv.innerHTML = '<p style="text-align: center;">Loading...</p>';
            
            try {
                const response = await fetch(`/api/user/rides/${currentUserId}`);
                const data = await response.json();
                
                if (!data.success || !data.data || data.data.length === 0) {
                    ridesDiv.innerHTML = '<p style="text-align: center; color: #999;">No rides yet</p>';
                    return;
                }
                
                ridesDiv.innerHTML = data.data.map(ride => `
                    <div class="ride-card">
                        <p><span class="status ${ride.status}">${ride.status.replace('_', ' ')}</span></p>
                        <p><strong>From:</strong> ${ride.source_location}</p>
                        <p><strong>To:</strong> ${ride.dest_location}</p>
                        <p><strong>Fare:</strong> ₹${ride.fare}</p>
                        ${ride.driver_name ? `<p><strong>Driver:</strong> ${ride.driver_name}</p>` : ''}
                        ${ride.status === 'requested' ? '<p style="color: #667eea; font-size: 12px; margin-top: 8px;">⏳ Waiting in queue...</p>' : ''}
                    </div>
                `).join('');
            } catch (error) {
                ridesDiv.innerHTML = '<p style="color: red;">Could not load rides</p>';
                console.error('Error loading rides:', error);
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(USER_DASHBOARD_HTML)

@app.route('/api/user/register', methods=['POST'])
def proxy_register_user():
    try:
        response = requests.post(
            f'{SERVER_URL}/api/users/register', 
            json=request.get_json(),
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Proxy error (register user): {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/user/request-ride-queue', methods=['POST'])
def proxy_request_ride_queue():
    try:
        response = requests.post(
            f'{SERVER_URL}/api/rides/request-with-queue', 
            json=request.get_json(),
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Proxy error (request ride): {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/user/queue-position/<int:ride_id>', methods=['GET'])
def proxy_queue_position(ride_id):
    try:
        response = requests.get(f'{SERVER_URL}/api/rides/{ride_id}/queue-position', timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Proxy error (queue position): {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/user/rides/<int:user_id>', methods=['GET'])
def proxy_user_rides(user_id):
    try:
        response = requests.get(f'{SERVER_URL}/api/users/{user_id}/rides', timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Proxy error (user rides): {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

if __name__ == '__main__':
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            sys.exit("Error: Invalid port number provided.")
    
    print(f'User Client running at http://localhost:{port}')
    print(f'Connecting to server at {SERVER_URL}')
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)