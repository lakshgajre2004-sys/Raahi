# 🚗 Raahi — Mini Uber Clone

Raahi is a full-stack ride-hailing web application built with Python and Flask, simulating a real-world Uber-like system. It features separate portals for users and drivers, an event booking system with ride integration, a round-robin load balancer across multiple backend servers, and a real-time admin dashboard.

---

## 🏗️ Architecture Overview

The Load Balancer (port **8090**) acts as the single entry point, routing requests using a **Round-Robin algorithm** across three Flask backend server instances (**3000, 3001, 3002**). All backend servers share a common PostgreSQL database (**miniuberdb**) through a connection pool, ensuring consistency and scalability.

### System Components

* **User Portal** – Book rides and event tickets.
* **Driver Portal** – Manage ride requests and ride status.
* **Load Balancer** – Distributes requests across backend servers.
* **Backend Servers** – Process ride, driver, user, and event operations.
* **PostgreSQL Database** – Stores all persistent data.
* **Admin Dashboard** – Monitors system activity and server health.

---

## 📁 Project Structure

| File                   | Description                                     |
| ---------------------- | ----------------------------------------------- |
| `complete-database.py` | Creates database schema and inserts sample data |
| `server.py`            | Core Flask REST API server                      |
| `loadbalancer.py`      | Round-robin load balancer with health checks    |
| `driver_client.py`     | Driver web interface                            |
| `user_client.py`       | User web interface                              |
| `serverdashboard.py`   | Administrative monitoring dashboard             |

---

## 🗃️ Database Schema

### Users Table

Stores registered riders.

### Drivers Table

Stores driver details, vehicle information, and online status.

### Rides Table

Stores ride requests, assignments, fares, and ride status.

### Events Table

Stores event information including venue, category, date, and pricing.

### Event Bookings Table

Stores ticket bookings and optional ride integration.

### Ride Skips Table

Tracks drivers who skip ride requests.

### Ride Lifecycle

```text
requested
    ↓
accepted
    ↓
in_progress
    ↓
completed

or

cancelled_by_user
cancelled_by_driver
```

---

## ⚙️ Features

### 👤 User Portal

* User authentication using User ID
* Ride booking between source and destination
* Fare estimation
* Event browsing and ticket booking
* Automatic ride generation for event bookings
* Real-time ride status updates

### 🚖 Driver Portal

* Driver authentication using Driver ID
* Online and offline status management
* Accept ride requests
* Skip ride requests
* Start rides
* Complete rides
* Real-time ride assignment system

### 🔄 Load Balancer

* Round-robin request distribution
* Three backend server instances
* Server health monitoring every 5 seconds
* Automatic unhealthy server detection
* HTTP keep-alive support
* Monitoring endpoint:

```text
/lb/status
```

### 📊 Admin Dashboard

* Monitor active rides
* View registered users
* View registered drivers
* Monitor events and bookings
* Observe request distribution
* Track backend server health

---

## 🚀 Installation & Setup

### Prerequisites

* Python 3.8+
* PostgreSQL
* Git

### Install Dependencies

```bash
pip install flask flask-cors psycopg psycopg-pool requests
```

---

## Step 1: Database Setup

```bash
python complete-database.py
```

Expected Output:

```text
Database ready with EVENT-RIDE integration
```

---

## Step 2: Start Backend Servers

Open three separate terminals.

### Terminal 1

```bash
python server.py 3000
```

### Terminal 2

```bash
python server.py 3001
```

### Terminal 3

```bash
python server.py 3002
```

---

## Step 3: Start Load Balancer

```bash
python loadbalancer.py
```

Load Balancer URL:

```text
http://localhost:8090
```

---

## Step 4: Launch User & Driver Portals

### Driver Portal

```bash
python driver_client.py
```

### User Portal

```bash
python user_client.py
```

---

## Step 5: Launch Admin Dashboard

```bash
python serverdashboard.py
```

---

## 🧪 Sample Data

### Users

| User ID | Name         |
| ------- | ------------ |
| 101     | Rohan Sharma |
| 102     | Anjali Verma |

### Drivers

| Driver ID | Name        | Vehicle      |
| --------- | ----------- | ------------ |
| 201       | Priya Singh | Maruti Swift |
| 202       | Raj Kumar   | Honda City   |

### Events

* Sunburn Music Festival
* TechCrunch Bangalore
* Comedy Night
* India vs Australia Cricket Match
* Food Truck Festival
* Diwali Mela
* Art Exhibition
* Yoga Retreat

---

## 🔧 Technologies Used

### Backend

* Python
* Flask
* Flask-CORS

### Database

* PostgreSQL
* Psycopg3
* Psycopg Connection Pool

### Networking

* HTTP
* REST APIs
* Round-Robin Load Balancing

### Frontend

* HTML
* CSS
* JavaScript

---

## 📈 Key Concepts Implemented

* Distributed Systems
* Load Balancing
* REST API Design
* Database Management
* Connection Pooling
* Event-Driven Booking System
* Ride Assignment Workflow
* Health Monitoring
* Client-Server Architecture

---

## 👨‍💻 Contributors

* Laksh Gajre
* Mohit Sah

GitHub:

* https://github.com/lakshgajre2004-sys
* https://github.com/MohitSah911

---

## 📜 License

This project is developed for educational and academic purposes as a Mini Uber Clone demonstrating distributed systems, database integration, and scalable web application design.
