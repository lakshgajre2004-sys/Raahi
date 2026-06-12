from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import sys

app = Flask(__name__)
CORS(app)

SERVER_URL = 'http://localhost:8080'

USER_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raahi - Ride with Us</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
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

        .auth-view {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            position: relative;
            z-index: 1;
        }

        .auth-container {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 24px;
            box-shadow: 0 40px 120px rgba(255, 255, 255, 0.1);
            overflow: hidden;
            max-width: 1000px;
            width: 100%;
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            min-height: 600px;
            animation: slideUp 0.6s ease-out;
            backdrop-filter: blur(20px);
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .auth-sidebar {
            background: #000000;
            padding: 60px 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }

        .auth-sidebar::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, transparent 100%);
            pointer-events: none;
        }

        .city-illustration {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 200px;
            opacity: 0.15;
            background: linear-gradient(to top, #000 0%, transparent 100%);
        }

        .city-illustration::before {
            content: "";
            position: absolute;
            bottom: 0;
            left: 10%;
            width: 20%;
            height: 120px;
            background: rgba(255,255,255,0.3);
            clip-path: polygon(0 100%, 50% 0, 100% 100%);
        }

        .city-illustration::after {
            content: "";
            position: absolute;
            bottom: 0;
            right: 15%;
            width: 25%;
            height: 100px;
            background: rgba(255,255,255,0.2);
            clip-path: polygon(0 100%, 30% 20%, 70% 30%, 100% 100%);
        }

        .logo-section {
            margin-bottom: 40px;
            position: relative;
            z-index: 1;
        }

        .raahi-logo {
            font-size: 56px;
            font-weight: 800;
            color: #fff;
            letter-spacing: 2px;
            margin-bottom: 16px;
            animation: fadeInLeft 0.8s ease-out;
            text-transform: uppercase;
            background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.8) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        @keyframes fadeInLeft {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }

        .tagline {
            font-size: 17px;
            color: rgba(255, 255, 255, 0.85);
            line-height: 1.7;
            animation: fadeInLeft 0.8s ease-out 0.2s both;
            font-weight: 600;
            font-style: italic;
        }

        .hindi-tagline {
            font-size: 15px;
            color: rgba(255, 255, 255, 0.7);
            margin-top: 12px;
            line-height: 1.6;
            animation: fadeInLeft 0.8s ease-out 0.3s both;
        }

        .feature-list {
            list-style: none;
            margin-top: 30px;
            position: relative;
            z-index: 1;
        }

        .feature-item {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 18px;
            color: rgba(255, 255, 255, 0.9);
            font-size: 15px;
            animation: fadeInLeft 0.8s ease-out 0.4s both;
        }

        .feature-icon {
            width: 28px;
            height: 28px;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            flex-shrink: 0;
        }

        .auth-content {
            padding: 60px 50px;
            background: #fff;
        }

        .auth-tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 40px;
            background: #f6f6f6;
            padding: 6px;
            border-radius: 12px;
        }

        .auth-tab {
            flex: 1;
            padding: 14px 24px;
            background: transparent;
            border: none;
            color: #666;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .auth-tab.active {
            background: #000;
            color: #fff;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .auth-form {
            display: none;
        }

        .auth-form.active {
            display: block;
            animation: fadeInUp 0.4s ease-out;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .form-group {
            margin-bottom: 24px;
        }

        label {
            display: block;
            margin-bottom: 10px;
            color: #000;
            font-weight: 600;
            font-size: 14px;
            letter-spacing: 0.3px;
        }

        input {
            width: 100%;
            padding: 16px 20px;
            border: 2px solid #e8e8e8;
            border-radius: 12px;
            font-size: 15px;
            transition: all 0.3s ease;
            background: #fafafa;
            color: #000;
        }

        input:focus {
            outline: none;
            border-color: #000;
            background: #fff;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            transform: translateY(-2px);
        }

        .btn {
            width: 100%;
            padding: 18px;
            background: #000;
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .btn::before {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }

        .btn:hover::before {
            width: 300px;
            height: 300px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .dashboard-view {
            min-height: 100vh;
            background: #000;
            position: relative;
            z-index: 1;
        }

        .dashboard-header {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            padding: 24px 40px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            animation: slideDown 0.5s ease-out;
        }

        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .welcome-section {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .user-avatar {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            border: 2px solid rgba(255,255,255,0.2);
        }

        .welcome-message {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.7) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .logout-btn {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 12px 28px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .logout-btn:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(255, 255, 255, 0.1);
        }

        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }

        .map-panel {
            grid-column: 1 / -1;
            padding: 0;
            border-radius: 20px;
            overflow: hidden;
            height: 350px;
            position: relative;
            animation: fadeInScale 0.5s ease-out both;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }

        #bengaluru-map {
            width: 100%;
            height: 100%;
            z-index: 1;
        }

        .map-overlay {
            position: absolute;
            top: 20px;
            left: 20px;
            background: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
            display: flex;
            align-items: center;
            gap: 12px;
            z-index: 1000;
        }

        .map-icon {
            font-size: 28px;
        }

        .map-text {
            display: flex;
            flex-direction: column;
        }

        .map-title {
            font-size: 18px;
            font-weight: 700;
            color: #000;
        }

        .map-subtitle {
            font-size: 13px;
            color: #666;
        }

        .panel {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            padding: 35px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            animation: fadeInScale 0.5s ease-out both;
            transition: all 0.3s ease;
        }

        .panel:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 40px rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.2);
        }

        @keyframes fadeInScale {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }

        .panel:nth-child(2) { animation-delay: 0.1s; }
        .panel:nth-child(3) { animation-delay: 0.2s; }

        .panel-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 28px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .panel-icon {
            width: 48px;
            height: 48px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }

        .panel h3 {
            font-size: 22px;
            font-weight: 700;
            color: #fff;
            margin: 0;
        }

        .alert {
            padding: 16px 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: none;
            animation: slideInAlert 0.4s ease-out;
            border-left: 4px solid;
        }

        @keyframes slideInAlert {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }

        .alert.success {
            background: rgba(76, 217, 100, 0.15);
            color: #4cd964;
            border-color: #4cd964;
        }

        .alert.error {
            background: rgba(255, 59, 48, 0.15);
            color: #ff3b30;
            border-color: #ff3b30;
        }

        .alert.show { display: block; }

        .location-input {
            position: relative;
            margin-bottom: 20px;
        }

        .location-icon {
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 20px;
            z-index: 1;
        }

        .location-input input {
            padding-left: 56px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #fff;
        }

        .location-input input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }

        .location-input input:focus {
            background: rgba(255, 255, 255, 0.12);
            border-color: rgba(255, 255, 255, 0.3);
        }

        /* Ride Status Tracker */
        .ride-status-tracker {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 40px;
            border-radius: 20px;
            margin-top: 30px;
            text-align: center;
            animation: fadeInScale 0.5s ease-out;
        }

        .status-icon-large {
            font-size: 80px;
            margin-bottom: 20px;
            animation: bounce 2s ease-in-out infinite;
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .status-title {
            font-size: 28px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 12px;
        }

        .status-message {
            font-size: 16px;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 24px;
            line-height: 1.6;
        }

        .loading-dots {
            display: inline-flex;
            gap: 8px;
            margin-top: 16px;
        }

        .loading-dot {
            width: 12px;
            height: 12px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 50%;
            animation: loadingPulse 1.4s ease-in-out infinite;
        }

        .loading-dot:nth-child(1) { animation-delay: 0s; }
        .loading-dot:nth-child(2) { animation-delay: 0.2s; }
        .loading-dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes loadingPulse {
            0%, 100% { opacity: 0.3; transform: scale(0.8); }
            50% { opacity: 1; transform: scale(1.2); }
        }

        .ride-details {
            background: rgba(255, 255, 255, 0.08);
            padding: 24px;
            border-radius: 16px;
            margin-top: 24px;
            text-align: left;
        }

        .ride-detail-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .ride-detail-row:last-child {
            border-bottom: none;
        }

        .ride-detail-label {
            color: rgba(255, 255, 255, 0.6);
            font-size: 14px;
        }

        .ride-detail-value {
            color: #fff;
            font-weight: 600;
            font-size: 15px;
        }

        .ride-fare {
            color: #4cd964;
            font-size: 24px;
            font-weight: 700;
        }

        .driver-info {
            background: linear-gradient(135deg, rgba(76, 217, 100, 0.2) 0%, rgba(76, 217, 100, 0.1) 100%);
            padding: 20px;
            border-radius: 14px;
            margin-top: 20px;
            border: 1px solid rgba(76, 217, 100, 0.3);
        }

        .driver-avatar {
            width: 60px;
            height: 60px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            margin: 0 auto 12px;
        }

        .driver-name {
            font-size: 20px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 4px;
        }

        .driver-arriving {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.8);
        }

        .ride-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 14px;
            margin-bottom: 16px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .ride-card::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: linear-gradient(180deg, #fff 0%, rgba(255, 255, 255, 0.5) 100%);
        }

        .ride-card:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateX(4px);
        }

        .ride-card p {
            margin: 10px 0;
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
        }

        .ride-card strong {
            color: #fff;
            font-weight: 600;
        }

        .ride-status {
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
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

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: rgba(255, 255, 255, 0.5);
        }

        .empty-icon {
            font-size: 64px;
            margin-bottom: 20px;
            opacity: 0.3;
        }

        @media (max-width: 968px) {
            .auth-container {
                grid-template-columns: 1fr;
            }
            .auth-sidebar {
                padding: 40px 30px;
            }
            .dashboard-container {
                grid-template-columns: 1fr;
            }
            .map-panel {
                height: 250px;
            }
        }
    </style>
</head>
<body>
    <div class="bg-pattern"></div>

    <!-- Authentication View -->
    <div id="auth-view" class="auth-view">
        <div class="auth-container">
            <div class="auth-sidebar">
                <div class="city-illustration"></div>
                <div class="logo-section">
                    <div class="raahi-logo">🚗 RAAHI</div>
                    <p class="tagline">Go anywhere with Raahi. Request a ride, hop in, and go.</p>
                    <p class="hindi-tagline">🛺 Auto wale se ho pareshan? Raahi use kro ghamasan! 💪</p>
                </div>
                <ul class="feature-list">
                    <li class="feature-item">
                        <span class="feature-icon">✨</span>
                        <span>Real-time ride tracking</span>
                    </li>
                    <li class="feature-item">
                        <span class="feature-icon">💰</span>
                        <span>Fair pricing estimates</span>
                    </li>
                    <li class="feature-item">
                        <span class="feature-icon">🛡️</span>
                        <span>Safe and reliable drivers</span>
                    </li>
                    <li class="feature-item">
                        <span class="feature-icon">🌟</span>
                        <span>24/7 customer support</span>
                    </li>
                </ul>
            </div>
            <div class="auth-content">
                <div class="auth-tabs">
                    <button class="auth-tab active" onclick="switchTab('register')">Sign Up</button>
                    <button class="auth-tab" onclick="switchTab('login')">Sign In</button>
                </div>

                <form id="register-form" class="auth-form active" onsubmit="registerUser(event)">
                    <div class="form-group">
                        <label>Full Name</label>
                        <input type="text" id="regName" placeholder="Enter your full name" required>
                    </div>
                    <div class="form-group">
                        <label>Email Address</label>
                        <input type="email" id="regEmail" placeholder="your.email@example.com" required>
                    </div>
                    <div class="form-group">
                        <label>Phone Number</label>
                        <input type="tel" id="regPhone" placeholder="+91 98765 43210" required>
                    </div>
                    <button type="submit" class="btn" id="registerBtn">Create Account</button>
                </form>

                <form id="login-form" class="auth-form" onsubmit="login(event)">
                    <div class="form-group">
                        <label>User ID</label>
                        <input type="number" id="loginUserId" placeholder="Enter your user ID" required>
                    </div>
                    <button type="submit" class="btn">Sign In</button>
                </form>
            </div>
        </div>
    </div>

    <!-- Dashboard View -->
    <div id="dashboard-view" class="dashboard-view" style="display: none;">
        <div class="dashboard-header">
            <div class="welcome-section">
                <div class="user-avatar">👤</div>
                <h2 id="welcome-message" class="welcome-message">Welcome!</h2>
            </div>
            <button class="logout-btn" onclick="logout()">
                <span>🚪</span>
                <span>Sign Out</span>
            </button>
        </div>

        <div class="dashboard-container">
            <!-- FREE OpenStreetMap -->
            <div class="map-panel">
                <div id="bengaluru-map"></div>
                <div class="map-overlay">
                    <span class="map-icon">📍</span>
                    <div class="map-text">
                        <div class="map-title">Bengaluru</div>
                        <div class="map-subtitle">Karnataka, India</div>
                    </div>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">
                    <div class="panel-icon">🚗</div>
                    <h3>Request a Ride</h3>
                </div>
                <div id="rideAlert" class="alert"></div>

                <form onsubmit="requestRide(event)" id="rideRequestForm">
                    <div class="location-input">
                        <span class="location-icon">📍</span>
                        <input type="text" id="source" placeholder="Enter pickup location" required>
                    </div>

                    <div class="location-input">
                        <span class="location-icon">🎯</span>
                        <input type="text" id="destination" placeholder="Enter destination" required>
                    </div>

                    <button type="submit" class="btn" id="rideBtn">Request Ride 🚀</button>
                </form>

                <!-- Ride Status Tracker -->
                <div id="rideStatusTracker" style="display: none;"></div>
            </div>

            <div class="panel">
                <div class="panel-header">
                    <div class="panel-icon">📋</div>
                    <h3>My Rides</h3>
                </div>
                <button onclick="loadMyRides()" class="btn" style="margin-bottom: 20px;">🔄 Refresh Rides</button>
                <div id="myRides">
                    <div class="empty-state">
                        <div class="empty-icon">🚕</div>
                        <p>Click refresh to load your rides</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentUserId = null;
        let currentUserName = null;
        let statusCheckInterval = null;
        let currentRideId = null;
        let map = null;

        // Initialize FREE OpenStreetMap
        function initMap() {
            if (map) return;

            map = L.map('bengaluru-map').setView([12.9716, 77.5946], 12);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(map);

            const locations = [
                {lat: 12.9716, lng: 77.5946, name: '🏛️ Vidhana Soudha', color: 'red'},
                {lat: 13.0827, lng: 77.5877, name: '✈️ Kempegowda Airport', color: 'blue'},
                {lat: 12.9352, lng: 77.6245, name: '🏢 Electronic City', color: 'green'},
                {lat: 12.9581, lng: 77.6348, name: '🛣️ Whitefield', color: 'orange'},
                {lat: 13.0067, lng: 77.5653, name: '🏛️ Cubbon Park', color: 'darkgreen'}
            ];

            locations.forEach(loc => {
                const icon = L.divIcon({
                    className: 'custom-marker',
                    html: `<div style="background: ${loc.color}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>`,
                    iconSize: [20, 20]
                });

                L.marker([loc.lat, loc.lng], {icon: icon})
                    .addTo(map)
                    .bindPopup(`<b>${loc.name}</b>`);
            });
        }

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

                localStorage.setItem(`user_${result.user_id}_name`, name);

                alert(`✅ Registration successful! Your User ID is ${result.user_id}`);
                switchTab('login');
                document.getElementById('loginUserId').value = result.user_id;
                document.getElementById('regName').value = '';
                document.getElementById('regEmail').value = '';
                document.getElementById('regPhone').value = '';

            } catch (error) {
                alert(`❌ Registration Error: ${error.message}`);
            } finally {
                registerBtn.disabled = false;
                registerBtn.textContent = 'Create Account';
            }
        }

        async function login(e) {
            e.preventDefault();
            const userId = document.getElementById('loginUserId').value;

            const storedName = localStorage.getItem(`user_${userId}_name`);
            currentUserName = storedName || `User ${userId}`;

            currentUserId = userId;
            document.getElementById('auth-view').style.display = 'none';
            document.getElementById('dashboard-view').style.display = 'block';
            document.getElementById('welcome-message').textContent = `Welcome, ${currentUserName}! 👋`;

            setTimeout(() => initMap(), 300);

            await loadMyRides();
            await checkForActiveRide();
        }

        function logout() {
            if (statusCheckInterval) {
                clearInterval(statusCheckInterval);
            }
            currentUserId = null;
            currentUserName = null;
            currentRideId = null;
            document.getElementById('auth-view').style.display = 'flex';
            document.getElementById('dashboard-view').style.display = 'none';
            document.getElementById('loginUserId').value = '';
            document.getElementById('source').value = '';
            document.getElementById('destination').value = '';
            document.getElementById('rideStatusTracker').style.display = 'none';
            document.getElementById('rideRequestForm').style.display = 'block';
        }

        async function requestRide(e) {
            e.preventDefault();
            const source = document.getElementById('source').value.trim();
            const destination = document.getElementById('destination').value.trim();

            const rideBtn = document.getElementById('rideBtn');
            rideBtn.disabled = true;
            rideBtn.textContent = 'Requesting Ride... ⏳';

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

                showAlert(`✅ Ride requested successfully!`, 'success');

                currentRideId = result.ride_id;

                // Hide form, show status tracker
                document.getElementById('rideRequestForm').style.display = 'none';
                displayRideStatus('requested', {
                    source,
                    destination,
                    fare: result.estimated_fare,
                    rideId: result.ride_id
                });

                // Start checking ride status
                startStatusCheck(result.ride_id);

                document.getElementById('source').value = '';
                document.getElementById('destination').value = '';

                loadMyRides();

            } catch (error) {
                showAlert(`❌ Ride Request Error: ${error.message}`, 'error');
            } finally {
                rideBtn.disabled = false;
                rideBtn.textContent = 'Request Ride 🚀';
            }
        }

        function displayRideStatus(status, rideData) {
            const tracker = document.getElementById('rideStatusTracker');
            tracker.style.display = 'block';

            let content = '';

            if (status === 'requested') {
                content = `
                    <div class="ride-status-tracker">
                        <div class="status-icon-large">🚗</div>
                        <div class="status-title">Ride Requested</div>
                        <div class="status-message">
                            Looking for available drivers nearby...<br>
                            Please wait while we find you a ride
                        </div>
                        <div class="loading-dots">
                            <div class="loading-dot"></div>
                            <div class="loading-dot"></div>
                            <div class="loading-dot"></div>
                        </div>
                        <div class="ride-details">
                            <div class="ride-detail-row">
                                <span class="ride-detail-label">📍 Pickup</span>
                                <span class="ride-detail-value">${rideData.source}</span>
                            </div>
                            <div class="ride-detail-row">
                                <span class="ride-detail-label">🎯 Destination</span>
                                <span class="ride-detail-value">${rideData.destination}</span>
                            </div>
                            <div class="ride-detail-row">
                                <span class="ride-detail-label">💰 Estimated Fare</span>
                                <span class="ride-fare">₹${rideData.fare}</span>
                            </div>
                        </div>
                    </div>
                `;
            } else if (status === 'accepted') {
                content = `
                    <div class="ride-status-tracker">
                        <div class="status-icon-large">✅</div>
                        <div class="status-title">Driver Accepted!</div>
                        <div class="status-message">
                            Your driver has accepted your ride request
                        </div>
                        <div class="driver-info">
                            <div class="driver-avatar">👨‍✈️</div>
                            <div class="driver-name">${rideData.driverName || 'Driver #' + rideData.driverId}</div>
                            <div class="driver-arriving">🚗 Driver is on the way to pick you up</div>
                        </div>
                        <div class="ride-details">
                            <div class="ride-detail-row">
                                <span class="ride-detail-label">📍 Pickup</span>
                                <span class="ride-detail-value">${rideData.source}</span>
                            </div>
                            <div class="ride-detail-row">
                                <span class="ride-detail-label">🎯 Destination</span>
                                <span class="ride-detail-value">${rideData.destination}</span>
                            </div>
                            <div class="ride-detail-row">
                                <span class="ride-detail-label">💰 Fare</span>
                                <span class="ride-fare">₹${rideData.fare}</span>
                            </div>
                        </div>
                    </div>
                `;
            } else if (status === 'in_progress') {
                content = `
                    <div class="ride-status-tracker">
                        <div class="status-icon-large">🚕</div>
                        <div class="status-title">Ride in Progress</div>
                        <div class="status-message">
                            You're on your way! Enjoy your ride
                        </div>
                        <div class="driver-info">
                            <div class="driver-avatar">👨‍✈️</div>
                            <div class="driver-name">${rideData.driverName || 'Driver #' + rideData.driverId}</div>
                            <div class="driver-arriving">🛣️ Taking you to your destination</div>
                        </div>
                        <div class="ride-details">
                            <div class="ride-detail-row">
                                <span class="ride-detail-label">📍 From</span>
                                <span class="ride-detail-value">${rideData.source}</span>
                            </div>
                            <div class="ride-detail-row">
                                <span class="ride-detail-label">🎯 To</span>
                                <span class="ride-detail-value">${rideData.destination}</span>
                            </div>
                            <div class="ride-detail-row">
                                <span class="ride-detail-label">💰 Fare</span>
                                <span class="ride-fare">₹${rideData.fare}</span>
                            </div>
                        </div>
                    </div>
                `;
            } else if (status === 'completed') {
                content = `
                    <div class="ride-status-tracker">
                        <div class="status-icon-large">🎉</div>
                        <div class="status-title">Ride Completed!</div>
                        <div class="status-message">
                            Thank you for riding with Raahi!<br>
                            Hope you had a great experience
                        </div>
                        <div class="ride-details">
                            <div class="ride-detail-row">
                                <span class="ride-detail-label">📍 From</span>
                                <span class="ride-detail-value">${rideData.source}</span>
                            </div>
                            <div class="ride-detail-row">
                                <span class="ride-detail-label">🎯 To</span>
                                <span class="ride-detail-value">${rideData.destination}</span>
                            </div>
                            <div class="ride-detail-row">
                                <span class="ride-detail-label">💰 Total Fare</span>
                                <span class="ride-fare">₹${rideData.fare}</span>
                            </div>
                        </div>
                        <button onclick="bookAnotherRide()" class="btn" style="margin-top: 20px;">Book Another Ride 🚀</button>
                    </div>
                `;
            }

            tracker.innerHTML = content;
        }

        function bookAnotherRide() {
            document.getElementById('rideStatusTracker').style.display = 'none';
            document.getElementById('rideRequestForm').style.display = 'block';
            if (statusCheckInterval) {
                clearInterval(statusCheckInterval);
                statusCheckInterval = null;
            }
            currentRideId = null;
        }

        function startStatusCheck(rideId) {
            if (statusCheckInterval) clearInterval(statusCheckInterval);

            statusCheckInterval = setInterval(async () => {
                try {
                    const response = await fetch(`/api/user/ride-status/${rideId}`);
                    const data = await response.json();

                    if (data.success && data.data) {
                        const ride = data.data;

                        if (ride.status !== 'requested') {
                            displayRideStatus(ride.status, {
                                source: ride.source_location,
                                destination: ride.dest_location,
                                fare: ride.fare,
                                driverId: ride.driver_id,
                                driverName: ride.driver_name
                            });
                        }

                        if (ride.status === 'completed') {
                            clearInterval(statusCheckInterval);
                            statusCheckInterval = null;
                            currentRideId = null;
                            loadMyRides();
                        }
                    }
                } catch (error) {
                    console.error('Error checking status:', error);
                }
            }, 2000); // Check every 2 seconds
        }

        async function checkForActiveRide() {
            try {
                const response = await fetch(`/api/user/rides/${currentUserId}`);
                const data = await response.json();

                if (data.success && data.data) {
                    const activeRide = data.data.find(ride => 
                        ride.status === 'requested' || 
                        ride.status === 'accepted' || 
                        ride.status === 'in_progress'
                    );

                    if (activeRide) {
                        currentRideId = activeRide.id;
                        document.getElementById('rideRequestForm').style.display = 'none';
                        displayRideStatus(activeRide.status, {
                            source: activeRide.source_location,
                            destination: activeRide.dest_location,
                            fare: activeRide.fare,
                            rideId: activeRide.id,
                            driverId: activeRide.driver_id,
                            driverName: activeRide.driver_name
                        });
                        startStatusCheck(activeRide.id);
                    }
                }
            } catch (error) {
                console.error('Error checking for active ride:', error);
            }
        }

        async function loadMyRides() {
            const ridesDiv = document.getElementById('myRides');
            ridesDiv.innerHTML = '<p style="text-align: center; color: rgba(255,255,255,0.5);">Loading... ⏳</p>';

            try {
                const response = await fetch(`/api/user/rides/${currentUserId}`);
                const data = await response.json();

                if (!data.success || !data.data || data.data.length === 0) {
                    ridesDiv.innerHTML = '<div class="empty-state"><div class="empty-icon">🚕</div><p>No rides yet</p></div>';
                    return;
                }

                ridesDiv.innerHTML = data.data.map(ride => `
                    <div class="ride-card">
                        <p><span class="ride-status status-${ride.status}">${ride.status.replace('_', ' ')}</span></p>
                        <p><strong>📍 From:</strong> ${ride.source_location}</p>
                        <p><strong>🎯 To:</strong> ${ride.dest_location}</p>
                        <p><strong>💰 Fare:</strong> ₹${ride.fare}</p>
                        ${ride.driver_name ? `<p><strong>👨‍✈️ Driver:</strong> ${ride.driver_name}</p>` : ''}
                    </div>
                `).join('');
            } catch (error) {
                ridesDiv.innerHTML = '<p style="color: #ff3b30;">❌ Could not load rides</p>';
                console.error('Error loading rides:', error);
            }
        }
    </script>
</body>
</html>
'''

# Flask routes remain the same
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

@app.route('/api/user/ride-status/<int:ride_id>', methods=['GET'])
def proxy_ride_status(ride_id):
    try:
        response = requests.get(f'{SERVER_URL}/api/rides/{ride_id}', timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Proxy error (ride status): {e}")
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

    print(f'🚗 Raahi User Client running at http://localhost:{port}')
    print(f'🗺️  Using FREE OpenStreetMap (No API Key Required!)')
    print(f'Connecting to server at {SERVER_URL}')
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)