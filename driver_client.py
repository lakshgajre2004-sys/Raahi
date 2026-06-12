from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import sys

app = Flask(__name__)
CORS(app)

SERVER_URL = 'http://localhost:8080'

DRIVER_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raahi Driver - Partner Portal</title>
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
            margin-bottom: 8px;
            animation: fadeInLeft 0.8s ease-out;
            text-transform: uppercase;
            background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.8) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .driver-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.15);
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 20px;
            animation: fadeInLeft 0.8s ease-out 0.1s both;
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

        .driver-avatar {
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

        .header-actions {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .status-toggle-container {
            display: flex;
            align-items: center;
            gap: 15px;
            background: rgba(255, 255, 255, 0.05);
            padding: 10px 20px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .status-label {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.7);
        }

        .switch {
            position: relative;
            width: 60px;
            height: 34px;
        }

        .switch input { 
            opacity: 0; 
            width: 0; 
            height: 0; 
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0; 
            left: 0; 
            right: 0; 
            bottom: 0;
            background-color: rgba(255, 255, 255, 0.2);
            transition: .4s;
            border-radius: 34px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }

        input:checked + .slider { 
            background-color: #4cd964; 
        }

        input:checked + .slider:before { 
            transform: translateX(26px); 
        }

        .status-text {
            font-weight: 700;
            font-size: 16px;
            min-width: 70px;
        }

        .status-text.offline { color: #ff3b30; }
        .status-text.online { color: #4cd964; }

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
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
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

        #driver-map {
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
        .panel:nth-child(4) { animation-delay: 0.3s; }

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

        .earnings-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 20px;
        }

        .earning-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
            padding: 20px;
            border-radius: 14px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }

        .earning-card:hover {
            transform: translateY(-4px);
            background: rgba(255, 255, 255, 0.12);
        }

        .earning-number {
            font-size: 32px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 8px;
        }

        .earning-label {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.6);
        }

        /* Single Next Ride Card */
        .next-ride-card {
            background: linear-gradient(135deg, rgba(76, 217, 100, 0.15) 0%, rgba(76, 217, 100, 0.05) 100%);
            border: 2px solid rgba(76, 217, 100, 0.3);
            padding: 30px;
            border-radius: 16px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .next-ride-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #4cd964, rgba(76, 217, 100, 0.5));
            animation: shimmer 2s infinite;
        }

        @keyframes shimmer {
            0%, 100% { transform: translateX(-100%); }
            50% { transform: translateX(100%); }
        }

        .next-ride-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 32px rgba(76, 217, 100, 0.2);
        }

        .ride-badge {
            display: inline-block;
            background: rgba(76, 217, 100, 0.2);
            color: #4cd964;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 16px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .ride-detail {
            margin: 16px 0;
            color: rgba(255, 255, 255, 0.9);
            font-size: 15px;
        }

        .ride-detail strong {
            color: #fff;
            font-weight: 600;
            margin-right: 8px;
        }

        .ride-fare-big {
            color: #4cd964;
            font-size: 36px;
            font-weight: 700;
            margin: 20px 0;
            text-align: center;
        }

        .ride-btn {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 16px;
            cursor: pointer;
            margin-top: 16px;
            transition: all 0.3s ease;
        }

        .accept-btn {
            background: #4cd964;
            color: #000;
        }

        .accept-btn:hover {
            background: #5ae374;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(76, 217, 100, 0.4);
        }

        .progress-btn {
            background: #5ac8fa;
            color: #000;
        }

        .progress-btn:hover {
            background: #6ad4ff;
            transform: translateY(-2px);
        }

        .complete-btn {
            background: rgba(255, 255, 255, 0.15);
            color: #fff;
        }

        .complete-btn:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
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
            background: linear-gradient(180deg, #4cd964 0%, rgba(76, 217, 100, 0.5) 100%);
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

        .ride-fare {
            color: #4cd964;
            font-size: 20px;
            font-weight: 700;
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

        .info-note {
            background: rgba(90, 200, 250, 0.15);
            border-left: 4px solid #5ac8fa;
            padding: 14px 18px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 13px;
            color: rgba(255, 255, 255, 0.8);
        }

        .loading-dots {
            display: inline-flex;
            gap: 8px;
        }

        .loading-dot {
            width: 10px;
            height: 10px;
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
            .header-actions {
                flex-direction: column;
                gap: 10px;
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
                    <div class="driver-badge">👨‍✈️ DRIVER PORTAL</div>
                    <p class="tagline">Join our platform and start earning by providing rides to passengers.</p>
                    <p class="hindi-tagline">🚕 Apne gaadi se kamao, har ride mein paao! 💪</p>
                </div>
                <ul class="feature-list">
                    <li class="feature-item">
                        <span class="feature-icon">💰</span>
                        <span>Earn money on your schedule</span>
                    </li>
                    <li class="feature-item">
                        <span class="feature-icon">📱</span>
                        <span>Easy-to-use driver app</span>
                    </li>
                    <li class="feature-item">
                        <span class="feature-icon">⚡</span>
                        <span>Instant ride notifications</span>
                    </li>
                    <li class="feature-item">
                        <span class="feature-icon">🎯</span>
                        <span>Fair queue-based system</span>
                    </li>
                </ul>
            </div>
            <div class="auth-content">
                <div class="auth-tabs">
                    <button class="auth-tab active" onclick="switchTab('login')">Sign In</button>
                    <button class="auth-tab" onclick="switchTab('register')">Sign Up</button>
                </div>

                <form id="login-form" class="auth-form active" onsubmit="login(event)">
                    <div class="form-group">
                        <label>Driver ID</label>
                        <input type="number" id="loginDriverId" placeholder="Enter your driver ID" required>
                    </div>
                    <button type="submit" class="btn">Sign In 🚗</button>
                </form>

                <form id="register-form" class="auth-form" onsubmit="registerDriver(event)">
                    <div class="form-group">
                        <label>Full Name</label>
                        <input type="text" id="regName" placeholder="Enter your full name" required>
                    </div>
                    <div class="form-group">
                        <label>Email Address</label>
                        <input type="email" id="regEmail" placeholder="your.email@example.com" required>
                    </div>
                    <div class="form-group">
                        <label>Vehicle Details</label>
                        <input type="text" id="regVehicle" placeholder="e.g., Maruti Swift (KA-01-AB-1234)" required>
                    </div>
                    <button type="submit" class="btn" id="registerBtn">Create Account 🚀</button>
                </form>
            </div>
        </div>
    </div>

    <!-- Dashboard View -->
    <div id="dashboard-view" class="dashboard-view" style="display: none;">
        <div class="dashboard-header">
            <div class="welcome-section">
                <div class="driver-avatar">👨‍✈️</div>
                <h2 id="welcome-message" class="welcome-message">Welcome!</h2>
            </div>
            <div class="header-actions">
                <div class="status-toggle-container">
                    <span class="status-label">Status:</span>
                    <label class="switch">
                        <input type="checkbox" id="onlineToggle" onchange="toggleOnlineStatus()">
                        <span class="slider"></span>
                    </label>
                    <span id="statusText" class="status-text offline">Offline</span>
                </div>
                <button class="logout-btn" onclick="logout()">
                    <span>🚪</span>
                    <span>Sign Out</span>
                </button>
            </div>
        </div>

        <div class="dashboard-container">
            <!-- FREE OpenStreetMap -->
            <div class="map-panel">
                <div id="driver-map"></div>
                <div class="map-overlay">
                    <span class="map-icon">🚗</span>
                    <div class="map-text">
                        <div class="map-title">Bengaluru Routes</div>
                        <div class="map-subtitle">Your service area</div>
                    </div>
                </div>
            </div>

            <!-- Current Ride Panel -->
            <div class="panel" id="current-ride-panel" style="display: none;">
                <div class="panel-header">
                    <div class="panel-icon">🎯</div>
                    <h3>Current Ride</h3>
                </div>
                <div id="current-ride-details"></div>
            </div>

            <!-- Next Available Ride Panel (SINGLE RIDE ONLY) -->
            <div class="panel" id="next-ride-panel" style="display: none;">
                <div class="panel-header">
                    <div class="panel-icon">🚀</div>
                    <h3>Next Ride Available</h3>
                </div>
                <div class="info-note">
                    ⚡ <strong>First-come, first-served</strong> - Accept quickly before another driver takes it!
                    <div class="loading-dots" style="margin-top: 8px;">
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                    </div>
                </div>
                <div id="next-ride-content"></div>
            </div>

            <!-- Earnings Summary Panel -->
            <div class="panel" id="summary-panel" style="display: none;">
                <div class="panel-header">
                    <div class="panel-icon">💰</div>
                    <h3>Today's Earnings</h3>
                </div>
                <div id="ride-summary" class="earnings-grid"></div>
                <button onclick="loadCompletedRides()" class="btn" style="margin-bottom: 20px;">🔄 Refresh Stats</button>
                <div id="completed-rides-list"></div>
            </div>
        </div>
    </div>

    <script>
        let currentDriverId = null;
        let currentDriverName = null;
        let queueRefreshInterval = null;
        let currentRideFare = 0;
        let driverMap = null;

        // Initialize FREE OpenStreetMap
        function initDriverMap() {
            if (driverMap) return;

            driverMap = L.map('driver-map').setView([12.9716, 77.5946], 12);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(driverMap);

            const locations = [
                {lat: 12.9716, lng: 77.5946, name: '🏛️ Vidhana Soudha', color: '#4cd964'},
                {lat: 13.0827, lng: 77.5877, name: '✈️ Airport', color: '#5ac8fa'},
                {lat: 12.9352, lng: 77.6245, name: '🏢 Electronic City', color: '#ffcc00'},
                {lat: 12.9581, lng: 77.6348, name: '🛣️ Whitefield', color: '#ff9500'},
                {lat: 13.0067, lng: 77.5653, name: '🌳 Cubbon Park', color: '#34c759'}
            ];

            locations.forEach(loc => {
                const icon = L.divIcon({
                    className: 'custom-marker',
                    html: `<div style="background: ${loc.color}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>`,
                    iconSize: [20, 20]
                });

                L.marker([loc.lat, loc.lng], {icon: icon})
                    .addTo(driverMap)
                    .bindPopup(`<b>${loc.name}</b>`);
            });
        }

        function switchTab(tab) {
            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));

            if (tab === 'login') {
                document.querySelectorAll('.auth-tab')[0].classList.add('active');
                document.getElementById('login-form').classList.add('active');
            } else {
                document.querySelectorAll('.auth-tab')[1].classList.add('active');
                document.getElementById('register-form').classList.add('active');
            }
        }

        async function login(e) {
            e.preventDefault();
            const driverId = document.getElementById('loginDriverId').value;

            try {
                const response = await fetch(`/api/driver/${driverId}`);
                const result = await response.json();
                if (!result.success) throw new Error(result.error);

                currentDriverId = driverId;
                const storedName = localStorage.getItem(`driver_${driverId}_name`);
                currentDriverName = storedName || result.data.name || `Driver ${driverId}`;

                document.getElementById('auth-view').style.display = 'none';
                document.getElementById('dashboard-view').style.display = 'block';
                document.getElementById('welcome-message').textContent = `Welcome, ${currentDriverName}! 👋`;
                document.getElementById('onlineToggle').checked = false;
                document.getElementById('statusText').textContent = 'Offline';
                document.getElementById('statusText').className = 'status-text offline';

                setTimeout(() => initDriverMap(), 300);
            } catch (error) {
                alert(`❌ Login Failed: ${error.message}`);
            }
        }

        function logout() {
            if (document.getElementById('onlineToggle').checked) {
                alert("⚠️ Please go offline before logging out.");
                return;
            }
            stopQueueAutoRefresh();
            currentDriverId = null;
            currentDriverName = null;
            document.getElementById('auth-view').style.display = 'flex';
            document.getElementById('dashboard-view').style.display = 'none';
            document.getElementById('loginDriverId').value = '';
        }

        async function registerDriver(e) {
            e.preventDefault();
            const name = document.getElementById('regName').value.trim();
            const email = document.getElementById('regEmail').value.trim();
            const vehicle = document.getElementById('regVehicle').value.trim();

            const registerBtn = document.getElementById('registerBtn');
            registerBtn.disabled = true;
            registerBtn.textContent = 'Creating Account...';

            try {
                const response = await fetch('/api/driver/register', { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json' }, 
                    body: JSON.stringify({ name, email, vehicle_details: vehicle }) 
                });
                const result = await response.json();

                if (!response.ok) throw new Error(result.details || result.error || 'Registration failed');

                localStorage.setItem(`driver_${result.driver_id}_name`, name);

                alert(`✅ Registration successful! Your Driver ID is ${result.driver_id}`);
                switchTab('login');
                document.getElementById('loginDriverId').value = result.driver_id;
                document.getElementById('regName').value = '';
                document.getElementById('regEmail').value = '';
                document.getElementById('regVehicle').value = '';
            } catch (error) { 
                alert(`❌ Registration Error: ${error.message}`); 
            } finally {
                registerBtn.disabled = false;
                registerBtn.textContent = 'Create Account 🚀';
            }
        }

        async function toggleOnlineStatus() {
            const toggle = document.getElementById('onlineToggle');
            const newStatus = toggle.checked ? 'online' : 'offline';

            try {
                const response = await fetch(`/api/driver/${currentDriverId}/status`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });

                const result = await response.json();
                if (!response.ok) throw new Error(result.error || 'Failed to update status');

                const statusText = document.getElementById('statusText');
                if (toggle.checked) {
                    statusText.textContent = 'Online';
                    statusText.className = 'status-text online';
                    checkActiveRide();
                    loadCompletedRides();
                    startQueueAutoRefresh();
                } else {
                    statusText.textContent = 'Offline';
                    statusText.className = 'status-text offline';
                    stopQueueAutoRefresh();
                    document.getElementById('current-ride-panel').style.display = 'none';
                    document.getElementById('next-ride-panel').style.display = 'none';
                    document.getElementById('summary-panel').style.display = 'none';
                }
            } catch (error) {
                alert(`❌ Error: ${error.message}`);
                toggle.checked = !toggle.checked;
            }
        }

        function startQueueAutoRefresh() {
            if (queueRefreshInterval) clearInterval(queueRefreshInterval);

            console.log('🔄 Starting auto-refresh for SINGLE next ride...');
            loadNextRide();
            queueRefreshInterval = setInterval(() => {
                loadNextRide();
            }, 2000); // Check every 2 seconds
        }

        function stopQueueAutoRefresh() {
            if (queueRefreshInterval) {
                clearInterval(queueRefreshInterval);
                queueRefreshInterval = null;
            }
        }

        async function checkActiveRide() {
            if (!currentDriverId) return;

            try {
                const response = await fetch(`/api/driver/${currentDriverId}/active-ride`);
                const data = await response.json();

                if (data.success && data.data) {
                    displayCurrentRide(data.data);
                } else if (document.getElementById('onlineToggle').checked) {
                    loadNextRide();
                }
            } catch (error) {
                console.error('Error checking active ride:', error);
            }
        }

        function displayCurrentRide(ride) {
            document.getElementById('next-ride-panel').style.display = 'none';
            const panel = document.getElementById('current-ride-panel');
            currentRideFare = ride.fare;

            let actionButton = '';
            if (ride.status === 'accepted') {
                actionButton = `<button class="ride-btn progress-btn" onclick="updateRideStatus(${ride.id}, 'in_progress')">🚀 Start Ride</button>`;
            } else if (ride.status === 'in_progress') {
                actionButton = `<button class="ride-btn complete-btn" onclick="updateRideStatus(${ride.id}, 'completed')">✅ Complete Ride</button>`;
            }

            document.getElementById('current-ride-details').innerHTML = `
                <div class="next-ride-card">
                    <div class="ride-badge">🎯 Active Ride</div>
                    <div class="ride-detail"><strong>📍 Pickup:</strong> ${ride.source_location}</div>
                    <div class="ride-detail"><strong>🎯 Drop:</strong> ${ride.dest_location}</div>
                    <div class="ride-fare-big">💰 ₹${ride.fare}</div>
                    ${actionButton}
                </div>
            `;
            panel.style.display = 'block';
        }

        async function updateRideStatus(rideId, newStatus) {
            try {
                const response = await fetch(`/api/driver/rides/${rideId}/update-status`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        driver_id: parseInt(currentDriverId), 
                        status: newStatus 
                    })
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Failed to update status');

                if (newStatus === 'completed') {
                    alert(`✅ Ride Completed! You earned ₹${currentRideFare} 💰`);
                    document.getElementById('current-ride-panel').style.display = 'none';
                    startQueueAutoRefresh();
                    loadCompletedRides();
                } else if (newStatus === 'accepted') {
                    stopQueueAutoRefresh();
                    checkActiveRide();
                } else {
                    alert(`✅ Status updated!`);
                    checkActiveRide();
                }
            } catch (error) {
                alert(`❌ Error: ${error.message}`);
            }
        }

        function acceptRide(rideId) {
            console.log('🎯 Accepting ride:', rideId);
            updateRideStatus(rideId, 'accepted');
        }

        async function loadNextRide() {
            if (!document.getElementById('onlineToggle').checked) return;

            // Check if driver has active ride first
            const activeResponse = await fetch(`/api/driver/${currentDriverId}/active-ride`);
            const activeData = await activeResponse.json();
            if (activeData.success && activeData.data) {
                displayCurrentRide(activeData.data);
                return;
            }

            document.getElementById('current-ride-panel').style.display = 'none';
            const panel = document.getElementById('next-ride-panel');
            panel.style.display = 'block';
            const contentDiv = document.getElementById('next-ride-content');

            try {
                const response = await fetch('/api/driver/rides/available');
                const data = await response.json();

                console.log('📋 Queue response:', data);

                if (!data.success || !data.data || data.data.length === 0) {
                    contentDiv.innerHTML = '<div class="empty-state"><div class="empty-icon">🚕</div><p>No rides waiting in queue<br><small style="font-size:13px;">Requests will appear here automatically</small></p></div>';
                    return;
                }

                // Show ONLY the first ride
                const nextRide = data.data[0];
                console.log('🚗 Showing first ride:', nextRide);

                contentDiv.innerHTML = `
                    <div class="next-ride-card">
                        <div class="ride-badge">🔥 Next in Queue</div>
                        <div class="ride-detail"><strong>📍 From:</strong> ${nextRide.source_location}</div>
                        <div class="ride-detail"><strong>🎯 To:</strong> ${nextRide.dest_location}</div>
                        <div class="ride-detail"><strong>👤 User:</strong> #${nextRide.user_id}</div>
                        <div class="ride-fare-big">💰 ₹${nextRide.fare}</div>
                        <button class="ride-btn accept-btn" onclick="acceptRide(${nextRide.id})">✅ Accept This Ride</button>
                    </div>
                `;
            } catch (error) {
                contentDiv.innerHTML = '<p style="color: #ff3b30; text-align:center;">❌ Could not connect to server</p>';
                console.error('Error:', error);
            }
        }

        async function loadCompletedRides() {
            if (!currentDriverId) return;

            const summaryPanel = document.getElementById('summary-panel');
            summaryPanel.style.display = 'block';
            const summaryDiv = document.getElementById('ride-summary');

            try {
                const response = await fetch(`/api/driver/${currentDriverId}/completed-rides`);
                const data = await response.json();

                if (!data.success) throw new Error(data.details || data.error || 'Unknown error');

                const summary = data.summary;
                summaryDiv.innerHTML = `
                    <div class="earning-card">
                        <div class="earning-number">${summary.total_rides}</div>
                        <div class="earning-label">🚗 Total Rides</div>
                    </div>
                    <div class="earning-card">
                        <div class="earning-number">₹${summary.total_earnings.toFixed(2)}</div>
                        <div class="earning-label">💰 Total Earnings</div>
                    </div>
                `;

                const listDiv = document.getElementById('completed-rides-list');
                if (data.data.length === 0) {
                    listDiv.innerHTML = '<div class="empty-state"><div class="empty-icon">📊</div><p>No completed rides today</p></div>';
                } else {
                    listDiv.innerHTML = '<h4 style="margin: 20px 0 15px 0; color: rgba(255,255,255,0.8);">Completed Today:</h4>' + 
                        data.data.map(ride => `
                        <div class="ride-card">
                            <p><strong>📍 From:</strong> ${ride.source_location}</p>
                            <p><strong>🎯 To:</strong> ${ride.dest_location}</p>
                            <p class="ride-fare">💰 ₹${ride.fare}</p>
                        </div>
                    `).join('');
                }
            } catch (error) {
                summaryDiv.innerHTML = `<p style="color:#ff3b30;">❌ Could not load: ${error.message}</p>`;
            }
        }
    </script>
</body>
</html>
'''

# Python proxy endpoints (unchanged)
@app.route('/')
def home():
    return render_template_string(DRIVER_DASHBOARD_HTML)

@app.route('/api/driver/<int:driver_id>', methods=['GET'])
def proxy_get_driver_details(driver_id):
    try:
        res = requests.get(f'{SERVER_URL}/api/drivers/{driver_id}')
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"Proxy error: {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/register', methods=['POST'])
def proxy_register_driver():
    try:
        res = requests.post(f'{SERVER_URL}/api/drivers/register', json=request.get_json())
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"Proxy error: {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/<int:driver_id>/status', methods=['PUT'])
def proxy_update_driver_status(driver_id):
    try:
        res = requests.put(f'{SERVER_URL}/api/drivers/{driver_id}/status', json=request.get_json())
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"Proxy error: {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/rides/available', methods=['GET'])
def proxy_get_available_rides():
    try:
        res = requests.get(f'{SERVER_URL}/api/rides/available')
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"Proxy error: {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/rides/<int:ride_id>/update-status', methods=['PUT'])
def proxy_update_ride_status(ride_id):
    try:
        res = requests.put(f'{SERVER_URL}/api/rides/{ride_id}/status', json=request.get_json())
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"Proxy error: {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/<int:driver_id>/active-ride', methods=['GET'])
def proxy_get_active_ride(driver_id):
    try:
        res = requests.get(f'{SERVER_URL}/api/drivers/{driver_id}/active-ride')
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"Proxy error: {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/<int:driver_id>/completed-rides', methods=['GET'])
def proxy_get_completed_rides(driver_id):
    try:
        res = requests.get(f'{SERVER_URL}/api/drivers/{driver_id}/completed-rides')
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"Proxy error: {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

if __name__ == '__main__':
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    print(f'🚗 Raahi Driver Portal (SINGLE RIDE QUEUE) running at http://localhost:{port}')
    print(f'🗺️  Using FREE OpenStreetMap (No API Key Required!)')
    print(f'Connecting to server at {SERVER_URL}')
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)