from flask import Flask, request, jsonify, render_template_string, Response
from flask_cors import CORS
import requests
import sys
import os
import json

app = Flask(__name__)
CORS(app)

# Allow overriding upstream server with env var for convenience
SERVER_URL = os.environ.get("RAAHI_SERVER_URL", "http://localhost:8090")

USER_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raahi - Ride with Us</title>
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

        .map-panel { display: none !important;
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
            .map-panel { display: none !important;
                height: 250px;
            }
        }
    

        /* EVENTS WITH REDUCED SPACING */
        .main-nav {
            display: flex;
            gap: 10px;
            max-width: 500px;
            margin: 0 auto 25px;
            background: rgba(255, 255, 255, 0.05);
            padding: 6px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .main-nav-tab {
            flex: 1;
            padding: 14px 20px;
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.6);
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            border-radius: 10px;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .main-nav-tab.active {
            background: #fff;
            color: #000;
            box-shadow: 0 4px 14px rgba(255, 255, 255, 0.2);
        }

        .section {
            display: none;
        }

        .section.active {
            display: block;
        }

        .panel {
            margin-bottom: 25px;
        }

        .events-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
            margin-top: 20px;
            padding: 10px 0;
        }

        .event-card {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 18px;
            overflow: hidden;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .event-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 16px 40px rgba(255, 255, 255, 0.12);
            border-color: rgba(255, 255, 255, 0.25);
        }

        .event-emoji {
            font-size: 56px;
            text-align: center;
            padding: 25px;
            background: rgba(255, 255, 255, 0.04);
        }

        .event-content {
            padding: 20px;
        }

        .event-category {
            display: inline-block;
            padding: 6px 14px;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            margin-bottom: 10px;
        }

        .event-title {
            font-size: 19px;
            font-weight: 800;
            margin-bottom: 10px;
            line-height: 1.3;
            color: #fff;
        }

        .event-description {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 14px;
            line-height: 1.6;
            min-height: 50px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .event-detail {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 6px;
        }

        .event-price {
            font-size: 24px;
            font-weight: 800;
            color: #4cd964;
            margin: 12px 0 14px;
        }

        .event-price.free {
            color: #ffcc00;
        }

        .book-btn {
            width: 100%;
            padding: 14px;
            background: #fff;
            color: #000;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .book-btn:hover {
            background: #f0f0f0;
            transform: translateY(-2px);
        }

        .booking-card {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 18px;
            border-radius: 16px;
            margin-bottom: 14px;
        }

        .booking-card p {
            margin: 6px 0;
            color: rgba(255, 255, 255, 0.85);
            font-size: 14px;
        }

        .booking-status {
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            background: rgba(76, 217, 100, 0.25);
            color: #4cd964;
            border: 1px solid rgba(76, 217, 100, 0.3);
        }

        /* Event Ride Features */
        .ride-badge {
            display: inline-block;
            padding: 4px 10px;
            background: rgba(76, 217, 100, 0.2);
            color: #4cd964;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
            margin-left: 8px;
        }

        .ride-status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 14px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            margin: 10px 0;
            font-size: 13px;
        }

        .action-btn {
            display: inline-block;
            padding: 10px 20px;
            background: #4cd964;
            color: #000;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 6px 4px;
        }

        .action-btn:hover {
            background: #3cb54a;
            transform: scale(1.05);
        }

        .action-btn.secondary {
            background: rgba(255, 255, 255, 0.15);
            color: #fff;
        }

        .action-btn.secondary:hover {
            background: rgba(255, 255, 255, 0.25);
        }

        .action-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        /* Modal for booking with ride */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }

        .modal.show {
            display: flex;
        }

        .modal-content {
            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
            border-radius: 20px;
            padding: 30px;
            max-width: 450px;
            width: 90%;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .modal-header {
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 20px;
            color: #fff;
        }

        .modal-option {
            padding: 18px;
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            margin-bottom: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .modal-option:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.3);
        }

        .modal-option.selected {
            background: rgba(76, 217, 100, 0.15);
            border-color: #4cd964;
        }

        .modal-option-title {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .modal-option-desc {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.6);
        }

        .input-group {
            margin: 16px 0;
        }

        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-size: 14px;
            font-weight: 600;
        }

        .input-group input {
            width: 100%;
            padding: 12px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            color: #fff;
            font-size: 14px;
        }

        .modal-actions {
            display: flex;
            gap: 12px;
            margin-top: 24px;
        }

        .modal-actions button {
            flex: 1;
            padding: 14px;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .modal-actions .btn-primary {
            background: #4cd964;
            color: #000;
        }

        .modal-actions .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
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

        <div class="main-nav">
        <button class="main-nav-tab active" onclick="switchMainSection('rides')">
          <span>🚗</span> Raahi Ride
        </button>
        <button class="main-nav-tab" onclick="switchMainSection('events')">
          <span>🎉</span> Raahi Events
        </button>
      </div>

      <div class="dashboard-container">
        <div id="rides-section" class="section active">
        
            <!-- FREE OpenStreetMap -->

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

    </div> <!-- End rides-section -->

      <div id="events-section" class="section">

        <!-- Scheduled Event Rides -->
        <div class="panel">
          <div class="panel-header">
            <div class="panel-icon">🚕</div>
            <h3>Scheduled Event Rides</h3>
          </div>
          <div id="scheduledRides">
            <div class="empty-state">
              <div class="empty-icon">🚕</div>
              <p>No scheduled event rides</p>
            </div>
          </div>
        </div>

        <!-- Discover Events -->
        <div class="panel">
          <div class="panel-header">
            <div class="panel-icon">🎉</div>
            <h3>Discover Events</h3>
          </div>
          <div id="eventsAlert" class="alert"></div>
          <div id="eventsGrid" class="events-grid">
            <p style="text-align: center; color: rgba(255,255,255,0.5); padding: 40px 0;">⏳ Loading events...</p>
          </div>
        </div>

        <!-- My Event Bookings -->
        <div class="panel">
          <div class="panel-header">
            <div class="panel-icon">🎫</div>
            <h3>My Event Bookings</h3>
          </div>
          <button onclick="loadMyEventBookings()" class="btn" style="margin-bottom: 18px;">
            🔄 Refresh Bookings
          </button>
          <div id="myEventBookings">
            <div class="empty-state">
              <div class="empty-icon">🎫</div>
              <p>No bookings yet</p>
            </div>
          </div>
        </div>
      </div> </div> <!-- End events-section -->

      <!-- Booking Modal -->
      <div id="bookingModal" class="modal">
        <div class="modal-content">
          <div class="modal-header">Book Event</div>

          <div class="input-group">
            <label>Number of Tickets:</label>
            <input type="number" id="modalTickets" value="1" min="1">
          </div>

          <div class="modal-option" onclick="selectBookingOption('event-only')">
            <div class="modal-option-title">🎫 Event Only</div>
            <div class="modal-option-desc">Just book the event ticket</div>
          </div>

          <div class="modal-option" onclick="selectBookingOption('with-ride')">
            <div class="modal-option-title">🚗 Book with Ride</div>
            <div class="modal-option-desc">Event ticket + rides to and from event</div>
          </div>

          <div id="pickupLocationGroup" class="input-group" style="display: none;">
            <label>Your Pickup Location:</label>
            <input type="text" id="modalPickupLocation" placeholder="Enter your location">
          </div>

          <div class="modal-actions">
            <button class="btn-secondary" onclick="closeBookingModal()">Cancel</button>
            <button class="btn-primary" onclick="confirmBooking()">Confirm Booking</button>
          </div>
        </div>
      </div>

      
      <script>
  let currentUserId = null;
  let currentUserName = null;
  let statusCheckTimeout = null;
  let currentRideId = null;

  // Helper to handle responses safely (JSON or non-JSON)
  async function handleResponse(response) {
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      const body = await response.json();
      if (!response.ok) {
        // Try to surface useful message
        const errMsg = body.error || body.message || JSON.stringify(body);
        throw new Error(errMsg);
      }
      return body;
    } else {
      const text = await response.text();
      console.error('Non-JSON response body:', text);
      throw new Error('Server returned non-JSON response: ' + text.slice(0, 400));
    }
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

      const result = await handleResponse(response);

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

      const result = await handleResponse(response);

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
    // --- NEW BLOCK: Handle No Drivers Found ---
    else if (status === 'cancelled_no_drivers') {
      content = `
          <div class="ride-status-tracker">
              <div class="status-icon-large" style="font-size: 60px;">😢</div>
              <div class="status-title" style="color: #ff3b30;">No Drivers Nearby</div>
              <div class="status-message">
                  We couldn't find a driver for you within 1 minute.<br>
                  Please try requesting again.
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
              </div>
              <button onclick="bookAnotherRide()" class="btn" style="margin-top: 20px; background: #333;">Try Again ↻</button>
          </div>
      `;
      // Stop the polling since the ride is essentially dead
      if (statusCheckTimeout) clearTimeout(statusCheckTimeout);
      currentRideId = null; 
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
    // 1. Clear any existing timeout to prevent duplicates
    if (statusCheckTimeout) clearTimeout(statusCheckTimeout);

    // 2. Define the checking logic
    const checkLoop = async () => {
        // Safety: Stop if we logged out or switched rides
        if (!currentRideId || currentRideId !== rideId) return;

        try {
            const response = await fetch(`/api/user/ride-status/${rideId}`);
            const data = await handleResponse(response);

            if (data.success && data.data) {
                let ride = data.data;
                if (Array.isArray(ride)) ride = ride[0];

                if (ride && ride.status !== 'requested') {
                    displayRideStatus(ride.status, {
                        source: ride.source_location,
                        destination: ride.dest_location,
                        fare: ride.fare,
                        driverId: ride.driver_id,
                        driverName: ride.driver_name
                    });
                }

                if (ride && ride.status === 'completed') {
                    currentRideId = null;
                    loadMyRides();
                    return; // STOP RECURSION here
                }
            }
        } catch (error) {
            console.error('Status check error:', error);
        }

        // 3. RECURSIVE CALL: Only schedule the NEXT check after this one finishes
        statusCheckTimeout = setTimeout(checkLoop, 2000);
    };

    // 4. Start the loop
    checkLoop();
}

  async function checkForActiveRide() {
    try {
      const response = await fetch(`/api/user/rides/${currentUserId}`);
      const data = await handleResponse(response);

      if (data.success && data.data) {
  // data.data may be an array (list of rides) or an object (single ride)
  let rides = data.data;
  if (!Array.isArray(rides)) rides = [rides];

  const activeRide = rides.find(ride =>
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
      const data = await handleResponse(response);

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

  // ========== EVENT + RIDE INTEGRATION SYSTEM ==========
  let currentBookingEvent = null;
  let selectedBookingOption = 'event-only';

  function switchMainSection(section) {
    document.querySelectorAll('.main-nav-tab').forEach(tab => tab.classList.remove('active'));
    event.target.closest('.main-nav-tab').classList.add('active');

    document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
    document.getElementById(section + '-section').classList.add('active');

    if (section === 'events') {
      loadEvents();
      loadScheduledEventRides();
      loadMyEventBookings();
    } else if (section === 'rides') {
      loadMyRides();
      checkForActiveRide();
    }
  }

  async function loadEvents() {
    const eventsGrid = document.getElementById('eventsGrid');
    eventsGrid.innerHTML = '<p style="text-align: center; color: rgba(255,255,255,0.5); padding: 40px 0;">⏳ Loading...</p>';

    try {
      const response = await fetch(`/api/events`);
      const data = await handleResponse(response);

      if (!data.success || !data.data || data.data.length === 0) {
        eventsGrid.innerHTML = '<div class="empty-state"><div class="empty-icon">🎉</div><p>No events available</p></div>';
        return;
      }

      eventsGrid.innerHTML = data.data.map(event => {
        const price = parseFloat(event.price);
        const priceDisplay = price === 0
          ? '<div class="event-price free">FREE</div>'
          : `<div class="event-price">₹${price.toFixed(0)}</div>`;

        return `
            <div class="event-card">
              <div class="event-emoji">${event.image_emoji || '🎉'}</div>
              <div class="event-content">
                <span class="event-category">${event.category || 'Event'}</span>
                <div class="event-title">${event.title}</div>
                <div class="event-description">${event.description}</div>
                <div class="event-detail"><span>📅</span> ${new Date(event.event_date).toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' })}</div>
                <div class="event-detail"><span>⏰</span> ${event.event_time || 'TBA'}</div>
                <div class="event-detail"><span>📍</span> ${event.location}</div>
                <div class="event-detail"><span>🎫</span> ${event.available_seats} seats</div>
                ${priceDisplay}
                <button class="book-btn" onclick='openBookingModal(${JSON.stringify(event)})'>
                  🎟️ Book Now
                </button>
              </div>
            </div>
        `;
      }).join('');
    } catch (error) {
      console.error('Error loading events:', error);
      eventsGrid.innerHTML = '<p style="color: #ff3b30; text-align: center;">Could not load events</p>';
    }
  }

  function openBookingModal(event) {
    if (!currentUserId) {
      showEventAlert('⚠️ Please login first', 'error');
      return;
    }

    currentBookingEvent = event;
    document.getElementById('modalTickets').value = 1;
    document.getElementById('modalPickupLocation').value = '';
    selectedBookingOption = 'event-only';

    // Reset option selection
    document.querySelectorAll('.modal-option').forEach(opt => opt.classList.remove('selected'));
    document.getElementById('pickupLocationGroup').style.display = 'none';

    document.getElementById('bookingModal').classList.add('show');
  }

  function closeBookingModal() {
    document.getElementById('bookingModal').classList.remove('show');
    currentBookingEvent = null;
  }

  function selectBookingOption(option) {
    selectedBookingOption = option;

    document.querySelectorAll('.modal-option').forEach(opt => opt.classList.remove('selected'));
    event.target.closest('.modal-option').classList.add('selected');

    if (option === 'with-ride') {
      document.getElementById('pickupLocationGroup').style.display = 'block';
    } else {
      document.getElementById('pickupLocationGroup').style.display = 'none';
    }
  }

  async function confirmBooking() {
    if (!currentBookingEvent) return;

    const numTickets = parseInt(document.getElementById('modalTickets').value);
    const withRide = selectedBookingOption === 'with-ride';
    const pickupLocation = document.getElementById('modalPickupLocation').value.trim();

    if (numTickets < 1) {
      alert('Please enter valid number of tickets');
      return;
    }

    if (withRide && !pickupLocation) {
      alert('Please enter your pickup location');
      return;
    }

    try {
      const response = await fetch(`/api/events/book`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: parseInt(currentUserId),
          event_id: currentBookingEvent.id,
          num_tickets: numTickets,
          with_ride: withRide,
          pickup_location: pickupLocation
        })
      });

      const result = await handleResponse(response);

      closeBookingModal();
      showEventAlert(`✅ ${result.message}`, 'success');

      loadEvents();
      loadScheduledEventRides();
      loadMyEventBookings();

    } catch (error) {
      showEventAlert(`❌ ${error.message}`, 'error');
    }
  }

  async function loadScheduledEventRides() {
    if (!currentUserId) return;

    const container = document.getElementById('scheduledRides');
    container.innerHTML = '<p style="text-align: center; color: rgba(255,255,255,0.5); padding: 30px 0;">⏳ Loading...</p>';

    try {
      const response = await fetch(`/api/users/${currentUserId}/event-bookings`);
      const data = await handleResponse(response);

      if (!data.success || !data.data) {
        container.innerHTML = '<div class="empty-state"><div class="empty-icon">🚕</div><p>No scheduled event rides</p></div>';
        return;
      }

      // 1. UPDATE FILTER: Added 'at_event' so the card stays visible after drop-off
      const scheduled = data.data.filter(b =>
        b.with_ride && ['scheduled', 'to_event', 'at_event', 'from_event'].includes(b.ride_status)
      );

      if (scheduled.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="empty-icon">🚕</div><p>No scheduled event rides</p></div>';
        return;
      }

      container.innerHTML = scheduled.map(booking => {
        let actionButton = '';
        let statusText = '';

        // 2. LOGIC UPDATE: Handle states specifically
        if (booking.ride_status === 'scheduled') {
          // State: Ride booked, not started
          statusText = '🕒 Ride Scheduled';
          actionButton = `<button class="action-btn" onclick="startEventRide(${booking.id})">🚗 Start Ride to Event</button>`;
        
        } else if (booking.ride_status === 'to_event') {
          // State: In the car (BUTTON HIDDEN)
          statusText = '🚖 On way to event...';
          actionButton = `<div style="padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; font-size: 13px; opacity: 0.7; text-align: center;">Wait for drop-off to book return 🛑</div>`;
        
        } else if (booking.ride_status === 'at_event') {
          // State: Dropped off (BUTTON APPEARS)
          statusText = '📍 You are at the Event';
          actionButton = `<button class="action-btn secondary" onclick="markEventComplete(${booking.id})">🏠 Request Return Ride</button>`;
        
        } else if (booking.ride_status === 'from_event') {
          // State: Going home
          statusText = '🏠 Return ride in progress...';
          actionButton = `<div style="font-size: 13px; color: #4cd964;">Have a safe journey home!</div>`;
        }

        return `
          <div class="booking-card">
            <p style="font-size: 17px; font-weight: 700;">${booking.event_emoji || '🎉'} ${booking.event_title}</p>
            <div class="ride-status-indicator">
              <span>${statusText}</span>
            </div>
            <p>📅 ${new Date(booking.event_date).toLocaleDateString('en-IN')}</p>
            <p>📍 From: ${booking.pickup_location}</p>
            <p>📍 To: ${booking.event_location}</p>
            ${actionButton}
          </div>
        `;
      }).join('');

    } catch (error) {
      console.error('Error:', error);
      container.innerHTML = '<p style="color: #ff3b30; text-align: center;">Could not load rides</p>';
    }
  }

  async function startEventRide(bookingId) {
  try {
    const response = await fetch(`/api/event-bookings/${bookingId}/start-ride`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });

    // Try to parse JSON or handle non-JSON error
    const contentType = response.headers.get('content-type') || '';
    let result;
    if (contentType.includes('application/json')) {
      result = await response.json();
      if (!response.ok) throw new Error(result.error || result.message || JSON.stringify(result));
    } else {
      const text = await response.text();
      throw new Error('Server returned non-JSON: ' + text.slice(0, 400));
    }

    showEventAlert(`✅ ${result.message}`, 'success');
    await loadScheduledEventRides();
    await loadMyEventBookings();
  } catch (err) {
    // If ride doesn't exist or wrong state, refresh bookings and show friendly error
    console.warn('startEventRide error', err);
    await loadScheduledEventRides();
    await loadMyEventBookings();
    showEventAlert(`❌ Error: ${err.message}`, 'error');
  }
}

async function markEventComplete(bookingId) {
  if (!confirm('Mark event as complete and request return ride?')) return;

  try {
    const response = await fetch(`/api/event-bookings/${bookingId}/mark-complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });

    const contentType = response.headers.get('content-type') || '';
    let result;
    if (contentType.includes('application/json')) {
      result = await response.json();
      if (!response.ok) throw new Error(result.error || result.message || JSON.stringify(result));
    } else {
      const text = await response.text();
      throw new Error('Server returned non-JSON: ' + text.slice(0, 400));
    }

    showEventAlert(`✅ ${result.message}`, 'success');
    await loadScheduledEventRides();
    await loadMyEventBookings();
  } catch (err) {
    console.warn('markEventComplete error', err);
    await loadScheduledEventRides();
    await loadMyEventBookings();
    showEventAlert(`❌ Error: ${err.message}`, 'error');
  }
}

  async function loadMyEventBookings() {
    if (!currentUserId) return;

    const container = document.getElementById('myEventBookings');
    container.innerHTML = '<p style="text-align: center; color: rgba(255,255,255,0.5); padding: 30px 0;">⏳ Loading...</p>';

    try {
      const response = await fetch(`/api/users/${currentUserId}/event-bookings`);
      const data = await handleResponse(response);

      if (!data.success || !data.data || data.data.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="empty-icon">🎫</div><p>No bookings yet</p></div>';
        return;
      }

      container.innerHTML = data.data.map(booking => {
        let rideBadge = '';
        let rideStatus = '';

        if (booking.with_ride) {
          const statusMap = {
            'scheduled': '🕒 Ride Scheduled',
            'to_event': '🚗 Going to Event',
            'at_event': '📍 At Event',
            'from_event': '🏠 Returning Home',
            'completed': '✅ Completed'
          };
          rideBadge = '<span class="ride-badge">WITH RIDE</span>';
          rideStatus = `<p style="font-size: 13px; color: #4cd964;">Ride: ${statusMap[booking.ride_status] || booking.ride_status}</p>`;
        }

        return `
          <div class="booking-card">
            <span class="booking-status">${booking.status}</span>
            ${rideBadge}
            <p style="font-size: 17px; font-weight: 700; margin-top: 10px;">${booking.event_emoji || '🎉'} ${booking.event_title}</p>
            <p>📅 ${new Date(booking.event_date).toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
            <p>⏰ ${booking.event_time || 'TBA'}</p>
            <p>📍 ${booking.event_location}</p>
            <p>🎫 Tickets: ${booking.num_tickets}</p>
            <p style="font-size: 18px; color: #4cd964; font-weight: 700; margin-top: 8px;">Total: ₹${parseFloat(booking.total_amount).toFixed(2)}</p>
            ${rideStatus}
            <p style="font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 10px;">Booked on ${new Date(booking.booking_date).toLocaleDateString('en-IN')}</p>
          </div>
        `;
      }).join('');

    } catch (error) {
      console.error('Error:', error);
      container.innerHTML = '<p style="color: #ff3b30; text-align: center;">Could not load bookings</p>';
    }
  }

  function showEventAlert(message, type = 'success') {
    const alert = document.getElementById('eventsAlert');
    if (alert) {
      alert.textContent = message;
      alert.className = `alert ${type} show`;
      setTimeout(() => alert.classList.remove('show'), 5000);
    }
  }
</script>

</body>
</html>
'''


def forward_response(resp):
    """
    Forward requests.Response 'resp' to the client.
    If backend sent valid JSON -> respond with that JSON + same status code.
    Otherwise forward raw text with original content-type and status code.
    """
    try:
        # Try to decode JSON
        body = resp.json()
        return jsonify(body), resp.status_code
    except ValueError:
        # Non-JSON (HTML/text/etc.) — forward raw
        content_type = resp.headers.get("Content-Type", "text/plain")
        return Response(resp.text, status=resp.status_code, content_type=content_type)

def safe_get_json(req):
    """Get JSON from incoming request without throwing."""
    try:
        payload = req.get_json(silent=True)
    except Exception:
        payload = None
    return payload or {}

# ---------------- Basic routes ----------------

@app.route('/')
def home():
    return render_template_string(USER_DASHBOARD_HTML)

# ------------- User / Ride Proxies --------------

@app.route('/api/user/register', methods=['POST'])
def proxy_register_user():
    try:
        payload = safe_get_json(request)
        resp = requests.post(f'{SERVER_URL}/api/users/register', json=payload, timeout=5)
        return forward_response(resp)
    except requests.exceptions.RequestException as e:
        app.logger.exception("Proxy error (register user)")
        return jsonify({'success': False, 'error': 'Server connection failed', 'detail': str(e)}), 503

@app.route('/api/user/request-ride-queue', methods=['POST'])
def proxy_request_ride_queue():
    try:
        payload = safe_get_json(request)
        resp = requests.post(f'{SERVER_URL}/api/rides/request-with-queue', json=payload, timeout=5)
        return forward_response(resp)
    except requests.exceptions.RequestException as e:
        app.logger.exception("Proxy error (request ride)")
        return jsonify({'success': False, 'error': 'Server connection failed', 'detail': str(e)}), 503

@app.route('/api/user/ride-status/<int:ride_id>', methods=['GET'])
def proxy_ride_status(ride_id):
    """
    Primary behaviour:
      1. Try GET /api/rides/{ride_id} on upstream (treat ride_id as ride id).
      2. If upstream returns 404 / "Ride not found" -> try treating the id as user_id:
           GET /api/users/{ride_id}/rides and return the first active/most recent ride (if any).
      3. Otherwise forward original response.
    This helps when the frontend sometimes passes a user id instead of a ride id.
    """
    try:
        # 1) Try as ride id
        resp = requests.get(f'{SERVER_URL}/api/rides/{ride_id}', timeout=5)
        if resp.status_code == 200:
            return forward_response(resp)

        # if backend says 404 / ride not found, attempt as user id
        # inspect JSON body if available
        try:
            body = resp.json()
            backend_error = body.get('error') or body.get('message') or ''
        except Exception:
            backend_error = None

        if resp.status_code in (404, ) or (backend_error and 'ride not found' in backend_error.lower()):
            # 2) treat ride_id as user_id and lookup user's rides
            try:
                user_resp = requests.get(f'{SERVER_URL}/api/users/{ride_id}/rides', timeout=5)
            except requests.exceptions.RequestException as e:
                app.logger.exception("Proxy error trying user rides fallback")
                return jsonify({'success': False, 'error': 'Server connection failed', 'detail': str(e)}), 503

            # If user_resp is OK and contains data, try to return an active ride
            if user_resp.status_code == 200:
                try:
                    ur_body = user_resp.json()
                    rides = ur_body.get('data')
                except Exception:
                    rides = None

                if isinstance(rides, dict):
                    # backend returned single ride object
                    return jsonify({'success': True, 'data': rides}), 200
                elif isinstance(rides, list) and len(rides) > 0:
                    # prefer active ride statuses
                    active = next((r for r in rides if r.get('status') in ('requested', 'accepted', 'in_progress')), None)
                    chosen = active or rides[0]
                    return jsonify({'success': True, 'data': chosen}), 200
                else:
                    return jsonify({'success': False, 'error': 'Ride not found'}), 404
            else:
                # upstream user rides returned non-200 — forward that
                return forward_response(user_resp)

        # Otherwise just forward the original resp (404 or other code)
        return forward_response(resp)

    except requests.exceptions.RequestException as e:
        app.logger.exception("Proxy error (ride status)")
        return jsonify({'success': False, 'error': 'Server connection failed', 'detail': str(e)}), 503

@app.route('/api/user/rides/<int:user_id>', methods=['GET'])
def proxy_user_rides(user_id):
    try:
        resp = requests.get(f'{SERVER_URL}/api/users/{user_id}/rides', timeout=5)
        return forward_response(resp)
    except requests.exceptions.RequestException as e:
        app.logger.exception("Proxy error (user rides)")
        return jsonify({'success': False, 'error': 'Server connection failed', 'detail': str(e)}), 503

# ------------- Events & Bookings --------------

@app.route("/api/events", methods=["GET"])
def proxy_get_events():
    try:
        resp = requests.get(f"{SERVER_URL}/api/events", timeout=5)
        return forward_response(resp)
    except requests.exceptions.RequestException as e:
        app.logger.exception("Proxy error (get events)")
        return jsonify({"success": False, "error": "Server connection failed", 'detail': str(e)}), 503

@app.route("/api/events/book", methods=["POST"])
def proxy_book_event():
    try:
        payload = safe_get_json(request)
        resp = requests.post(f"{SERVER_URL}/api/events/book", json=payload, timeout=5)
        return forward_response(resp)
    except requests.exceptions.RequestException as e:
        app.logger.exception("Proxy error (book event)")
        return jsonify({"success": False, "error": "Server connection failed", 'detail': str(e)}), 503

@app.route("/api/users/<int:user_id>/event-bookings", methods=["GET"])
def proxy_get_user_bookings(user_id):
    try:
        resp = requests.get(f"{SERVER_URL}/api/users/{user_id}/event-bookings", timeout=5)
        return forward_response(resp)
    except requests.exceptions.RequestException as e:
        app.logger.exception("Proxy error (get user bookings)")
        return jsonify({"success": False, "error": "Server connection failed", 'detail': str(e)}), 503

@app.route("/api/event-bookings/<int:booking_id>/start-ride", methods=["POST"])
def proxy_start_event_ride(booking_id):
    try:
        payload = safe_get_json(request)
        resp = requests.post(f"{SERVER_URL}/api/event-bookings/{booking_id}/start-ride", json=payload, timeout=5)
        return forward_response(resp)
    except requests.exceptions.RequestException as e:
        app.logger.exception("Proxy error (start_event_ride)")
        return jsonify({"success": False, "error": "Server connection failed", 'detail': str(e)}), 503

@app.route("/api/event-bookings/<int:booking_id>/mark-complete", methods=["POST"])
def proxy_mark_event_complete(booking_id):
    try:
        payload = safe_get_json(request)
        resp = requests.post(f"{SERVER_URL}/api/event-bookings/{booking_id}/mark-complete", json=payload, timeout=5)
        return forward_response(resp)
    except requests.exceptions.RequestException as e:
        app.logger.exception("Proxy error (mark_event_complete)")
        return jsonify({"success": False, "error": "Server connection failed", 'detail': str(e)}), 503

# ----- new: proxy GET for a single event-booking (you tried this earlier) -----
@app.route("/api/event-bookings/<int:booking_id>", methods=["GET"])
def proxy_get_event_booking(booking_id):
    try:
        resp = requests.get(f"{SERVER_URL}/api/event-bookings/{booking_id}", timeout=5)
        return forward_response(resp)
    except requests.exceptions.RequestException as e:
        app.logger.exception("Proxy error (get_event_booking)")
        return jsonify({"success": False, "error": "Server connection failed", 'detail': str(e)}), 503

# ------------------- RUN SERVER -------------------

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