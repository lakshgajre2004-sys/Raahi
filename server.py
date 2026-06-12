from flask import Flask, request, jsonify
from flask_cors import CORS
from psycopg.rows import dict_row
import psycopg
import random
import traceback  # Import the traceback module for better error logging

app = Flask(__name__)
CORS(app)

# --- Database Configuration ---
DB_NAME = "miniuberdb"
DB_USER = "postgres"
DB_PASS = "Laksh@2004"
DB_HOST = "localhost"
DB_PORT = "5432"


def get_db_connection():
    """Establishes a robust connection to the PostgreSQL database."""
    try:
        return psycopg.connect(
            f"user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT} dbname={DB_NAME}",
            autocommit=True
        )
    except psycopg.OperationalError as e:
        print(f"CRITICAL: Database connection failed: {e}")
        raise


# --- Fare Calculation Logic ---
def calculate_fare(source, destination):
    base_fare = 50.0
    rate_per_km = 12.5
    simulated_distance = max(1, (len(source) + len(destination)) / 2 + random.uniform(-2, 2))
    return round(base_fare + (simulated_distance * rate_per_km), 2)


# --- Driver Login Endpoint ---
@app.route('/api/drivers/<int:driver_id>', methods=['GET'])
def get_driver_details(driver_id):
    """Fetches details for a single driver to verify their existence."""
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT id, name FROM drivers WHERE id = %s;", (driver_id,))
                driver = cur.fetchone()

        if driver:
            return jsonify({'success': True, 'data': driver})
        else:
            return jsonify({'success': False, 'error': 'Driver not found'}), 404
    except Exception as e:
        print(f"Error in get_driver_details:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500


# --- Ride Lifecycle Endpoint ---
# --- Robust ride state change endpoint (replaced) ---
ALLOWED_TRANSITIONS = {
    'requested': ['accepted', 'cancelled_by_user'],
    'accepted': ['in_progress', 'cancelled_by_driver'],
    'in_progress': ['completed', 'cancelled_by_driver'],
    'completed': [],
    'cancelled_by_user': [],
    'cancelled_by_driver': []
}

@app.route('/api/rides/<int:ride_id>/status', methods=['PUT'])
def update_ride_status(ride_id):
    """
    Robust ride state updater:
    - validates input
    - locks the ride row (SELECT ... FOR UPDATE) to avoid races
    - validates allowed transitions
    - returns clear 4xx/5xx responses with details
    """
    try:
        data = request.get_json(silent=True) or {}
        driver_id = data.get('driver_id')
        new_status = data.get('status')
        actor = data.get('actor', 'unknown')

        if not new_status:
            return jsonify({'success': False, 'error': 'status (new state) is required'}), 400

        # Acquire DB row lock to prevent races
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT id, status, driver_id FROM rides WHERE id = %s FOR UPDATE", (ride_id,))
                row = cur.fetchone()

                if not row:
                    return jsonify({'success': False, 'error': 'ride_not_found', 'ride_id': ride_id}), 404

                current_status = row['status']
                current_driver = row.get('driver_id')

                print(f"[RideState] ride={ride_id} actor={actor} requested={new_status} current={current_status} cur_driver={current_driver} req_driver={driver_id}")

                # if driver_id is required for this transition, validate it
                if new_status in ('accepted', 'in_progress', 'completed'):
                    if not driver_id:
                        return jsonify({'success': False, 'error': 'driver_id required for this transition'}), 400

                # Validate allowed transition
                allowed_next = ALLOWED_TRANSITIONS.get(current_status, [])
                if new_status not in allowed_next:
                    return jsonify({
                        'success': False,
                        'error': 'invalid_state_transition',
                        'detail': {
                            'ride_id': ride_id,
                            'current_status': current_status,
                            'attempted': new_status,
                            'allowed_next': allowed_next
                        }
                    }), 400

                # Ownership check: only assigned driver can mark in_progress/completed
                if current_driver and new_status in ('in_progress', 'completed') and driver_id != current_driver:
                    return jsonify({'success': False, 'error': 'driver_mismatch', 'detail': {'current_driver': current_driver}}), 403

                # Build update SQL per state
                if new_status == 'accepted':
                    sql = "UPDATE rides SET driver_id = %s, status = 'accepted', updated_at = NOW() WHERE id = %s RETURNING id;"
                    params = (driver_id, ride_id)
                elif new_status == 'in_progress':
                    sql = "UPDATE rides SET status = 'in_progress', started_at = NOW(), updated_at = NOW() WHERE id = %s AND driver_id = %s RETURNING id;"
                    params = (ride_id, driver_id)
                elif new_status == 'completed':
                    sql = "UPDATE rides SET status = 'completed', completed_at = NOW(), updated_at = NOW() WHERE id = %s AND driver_id = %s RETURNING id;"
                    params = (ride_id, driver_id)
                else:
                    return jsonify({'success': False, 'error': 'unsupported_state'}), 400

                cur.execute(sql, params)
                updated = cur.fetchone()
                if not updated:
                    return jsonify({'success': False, 'error': 'update_failed', 'detail': 'Row not updated - possible concurrent modification or mismatched driver/state'}), 409

                # commit if needed (your connection may already autocommit)
                try:
                    conn.commit()
                except Exception:
                    pass

                print(f"✅ Ride {ride_id} -> {new_status} by driver {driver_id} (actor={actor})")
                return jsonify({'success': True, 'ride_id': ride_id, 'new_status': new_status}), 200

    except Exception as e:
        print("ERROR in update_ride_status:", e)
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'internal_server_error', 'details': str(e)}), 500
@app.route('/api/rides/request', methods=['POST'])
def request_ride():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['user_id', 'source_location', 'dest_location']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        user_id = data['user_id']
        fare = calculate_fare(data['source_location'], data['dest_location'])

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # --- FIX: Validate user_id exists before inserting ride ---
                cur.execute("SELECT id FROM users WHERE id = %s;", (user_id,))
                if not cur.fetchone():
                    return jsonify({'success': False, 'error': f'User with id {user_id} not found'}), 404

                cur.execute(
                    "INSERT INTO rides (user_id, source_location, dest_location, status, fare) "
                    "VALUES (%s, %s, %s, 'requested', %s) RETURNING id;",
                    (user_id, data['source_location'], data['dest_location'], fare)
                )
                # --- FIX: Safely fetch the result ---
                result = cur.fetchone()
                if result:
                    ride_id = result[0]
                else:
                    return jsonify({'success': False, 'error': 'Failed to create ride'}), 500

        return jsonify({'success': True, 'ride_id': ride_id, 'estimated_fare': fare}), 201
    except Exception as e:
        print(f"Error in request_ride:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500


# --- Ride Request with Queue Info ---
@app.route('/api/rides/request-with-queue', methods=['POST'])
def request_ride_with_queue():
    """Request a ride and get immediate queue information"""
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['user_id', 'source_location', 'dest_location']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        user_id = data['user_id']
        fare = calculate_fare(data['source_location'], data['dest_location'])

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # --- FIX: Validate user_id exists before inserting ride ---
                cur.execute("SELECT id FROM users WHERE id = %s;", (user_id,))
                if not cur.fetchone():
                    return jsonify({'success': False, 'error': f'User with id {user_id} not found'}), 404

                # Insert the ride
                cur.execute(
                    "INSERT INTO rides (user_id, source_location, dest_location, status, fare) "
                    "VALUES (%s, %s, %s, 'requested', %s) RETURNING id, created_at;",
                    (user_id, data['source_location'], data['dest_location'], fare)
                )
                result = cur.fetchone()
                if not result:
                    return jsonify({'success': False, 'error': 'Failed to create ride'}), 500

                ride_id = result[0]
                created_at = result[1]

                # Get queue position - count all requested rides created before or at same time
                cur.execute("SELECT COUNT(*) FROM rides WHERE status = 'requested' AND created_at <= %s;", (created_at,))
                queue_position_result = cur.fetchone()
                queue_position = queue_position_result[0] if queue_position_result else 1

                # Get online drivers
                cur.execute("SELECT COUNT(*) FROM drivers WHERE online_status = 'online'")
                online_drivers_result = cur.fetchone()
                online_drivers = online_drivers_result[0] if online_drivers_result else 0

        print(f"ðŸŽ« New ride #{ride_id} created - Queue position: {queue_position}, Online drivers: {online_drivers}")

        return jsonify({
            'success': True,
            'ride_id': ride_id,
            'estimated_fare': fare,
            'queue_position': queue_position,
            'online_drivers': online_drivers
        }), 201
    except Exception as e:
        print(f"Error in request_ride_with_queue:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500


# --- Get Queue Position ---
@app.route('/api/rides/<int:ride_id>/queue-position', methods=['GET'])
def get_queue_position(ride_id):
    """Get the position of a ride in the queue - REAL-TIME UPDATE"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # First check if ride exists and get its status
                cur.execute("SELECT id, status, created_at FROM rides WHERE id = %s", (ride_id,))
                ride = cur.fetchone()

                if not ride:
                    return jsonify({'success': False, 'error': 'Ride not found'}), 404

                if ride['status'] != 'requested':
                    print(f"ðŸ“ Ride {ride_id} status: {ride['status']} (not in queue)")
                    return jsonify({'success': True, 'status': ride['status'], 'in_queue': False})

                # --- FIX: Safely fetch COUNT results ---
                cur.execute("SELECT COUNT(*) FROM rides WHERE status = 'requested' AND created_at < %s", (ride['created_at'],))
                rides_before_result = cur.fetchone()
                # handle both tuple and dict_row results
                rides_before = rides_before_result[0] if isinstance(rides_before_result, tuple) else rides_before_result.get('count', 0)

                queue_position = rides_before + 1

                cur.execute("SELECT COUNT(*) FROM rides WHERE status = 'requested'")
                total_waiting_result = cur.fetchone()
                total_waiting = total_waiting_result[0] if isinstance(total_waiting_result, tuple) else total_waiting_result.get('count', 0)

                cur.execute("SELECT COUNT(*) FROM drivers WHERE online_status = 'online'")
                online_drivers_result = cur.fetchone()
                online_drivers = online_drivers_result[0] if isinstance(online_drivers_result, tuple) else online_drivers_result.get('count', 0)

                print(f"ðŸ“Š Ride {ride_id} - Position: {queue_position}/{total_waiting}, Drivers: {online_drivers}")

                return jsonify({
                    'success': True,
                    'queue_position': queue_position,
                    'total_waiting': total_waiting,
                    'online_drivers': online_drivers,
                    'in_queue': True,
                    'status': 'requested'
                })
    except Exception as e:
        print(f"Error in get_queue_position:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500


# --- Get All Rides for a User ---
@app.route('/api/users/<int:user_id>/rides', methods=['GET'])
def get_user_rides(user_id):
    """Get all rides for a user"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT r.*, d.name as driver_name 
                    FROM rides r
                    LEFT JOIN drivers d ON r.driver_id = d.id
                    WHERE r.user_id = %s 
                    ORDER BY r.created_at DESC
                """, (user_id,))
                rides = cur.fetchall()

                for ride in rides:
                    if ride.get('created_at'):
                        ride['created_at'] = ride['created_at'].isoformat()
                    if ride.get('completed_at'):
                        ride['completed_at'] = ride['completed_at'].isoformat()

                return jsonify({'success': True, 'data': rides})
    except Exception as e:
        print(f"Error in get_user_rides:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500


# --- Available Rides Endpoint (single, fixed implementation) ---
@app.route('/api/rides/available', methods=['GET'])
def get_available_rides():
    """Get all rides available for drivers (includes event rides)"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT * FROM rides 
                    WHERE status IN ('requested', 'waiting', 'event_to', 'event_from')
                    ORDER BY created_at ASC;
                """)
                rides = cur.fetchall()

                # Normalize timestamps for JSON
                for r in rides:
                    if r.get('created_at'):
                        r['created_at'] = r['created_at'].isoformat()

        print(f"ðŸ“‹ Available rides in queue: {len(rides)}")
        return jsonify({'success': True, 'data': rides})
    except Exception as e:
        print("Error in get_available_rides:", e)
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# --- Driver Status Endpoint ---
@app.route('/api/drivers/<int:driver_id>/status', methods=['PUT'])
def update_driver_status(driver_id):
    try:
        data = request.get_json()
        new_status = data.get('status')

        if not new_status:
            return jsonify({'success': False, 'error': 'Status is required'}), 400

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE drivers SET online_status = %s WHERE id = %s;", (new_status, driver_id))

        print(f"ðŸš— Driver {driver_id} is now {new_status}")
        return jsonify({'success': True, 'message': f'Driver is now {new_status}.'})
    except Exception as e:
        print(f"Error in update_driver_status:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500


# ==========================================
# ADMIN DASHBOARD ENDPOINTS
# ==========================================

# --- Get All Users ---
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    """Get all registered users for admin dashboard"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT id, name, email, phone, created_at FROM users ORDER BY created_at DESC;")
                users = cur.fetchall()

                for user in users:
                    if user.get('created_at'):
                        user['created_at'] = user['created_at'].isoformat()

                return jsonify({'success': True, 'data': users})
    except Exception as e:
        print(f"Error in get_all_users:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500


# --- Get All Drivers ---
@app.route('/api/admin/drivers', methods=['GET'])
def get_all_drivers():
    """Get all registered drivers with their status"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT id, name, email, vehicle_details, online_status, created_at FROM drivers ORDER BY created_at DESC;")
                drivers = cur.fetchall()

                for driver in drivers:
                    if driver.get('created_at'):
                        driver['created_at'] = driver['created_at'].isoformat()

                return jsonify({'success': True, 'data': drivers})
    except Exception as e:
        print(f"Error in get_all_drivers:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500


# --- Get All Rides ---
@app.route('/api/admin/rides', methods=['GET'])
def get_all_rides():
    """Get all rides with user and driver info"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT r.*, u.name as user_name, d.name as driver_name
                    FROM rides r
                    LEFT JOIN users u ON r.user_id = u.id
                    LEFT JOIN drivers d ON r.driver_id = d.id
                    ORDER BY r.created_at DESC
                    LIMIT 100;
                """)
                rides = cur.fetchall()

                for ride in rides:
                    if ride.get('created_at'):
                        ride['created_at'] = ride['created_at'].isoformat()
                    if ride.get('completed_at'):
                        ride['completed_at'] = ride['completed_at'].isoformat()

                return jsonify({'success': True, 'data': rides})
    except Exception as e:
        print(f"Error in get_all_rides:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500


# --- Get Dashboard Stats ---
@app.route('/api/admin/stats', methods=['GET'])
def get_dashboard_stats():
    """Get overall statistics for admin dashboard"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Total users
                cur.execute("SELECT COUNT(*) FROM users;")
                total_users = cur.fetchone()[0]

                # Total drivers
                cur.execute("SELECT COUNT(*) FROM drivers;")
                total_drivers = cur.fetchone()[0]

                # Online drivers
                cur.execute("SELECT COUNT(*) FROM drivers WHERE online_status = 'online';")
                online_drivers = cur.fetchone()[0]

                # Active rides (accepted or in_progress)
                cur.execute("SELECT COUNT(*) FROM rides WHERE status IN ('accepted', 'in_progress');")
                active_rides = cur.fetchone()[0]

                return jsonify({
                    'success': True,
                    'stats': {
                        'total_users': total_users,
                        'total_drivers': total_drivers,
                        'online_drivers': online_drivers,
                        'active_rides': active_rides
                    }
                })
    except Exception as e:
        print(f"Error in get_dashboard_stats:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500


@app.route('/api/rides/<int:ride_id>', methods=['GET'])
def get_ride_details(ride_id):
    """Get detailed information about a specific ride"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT r.*, 
                           u.name as user_name,
                           d.name as driver_name,
                           d.vehicle_details
                    FROM rides r
                    LEFT JOIN users u ON r.user_id = u.id
                    LEFT JOIN drivers d ON r.driver_id = d.id
                    WHERE r.id = %s;
                """, (ride_id,))

                ride = cur.fetchone()

                if not ride:
                    return jsonify({'success': False, 'error': 'Ride not found'}), 404

                # Convert timestamps to ISO format
                if ride.get('created_at'):
                    ride['created_at'] = ride['created_at'].isoformat()
                if ride.get('completed_at'):
                    ride['completed_at'] = ride['completed_at'].isoformat()

                return jsonify({'success': True, 'data': ride})

    except Exception as e:
        print(f"Error in get_ride_details:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500


# ============= ENHANCED EVENT + RIDE ENDPOINTS =============

@app.route("/api/events", methods=["GET"])
def get_all_events():
    """Get all available events"""
    try:
        print("ðŸ“¡ GET /api/events")
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT id, title, description, event_date, event_time, 
                           location, category, price, image_emoji, available_seats
                    FROM events ORDER BY event_date ASC
                """)
                events = cur.fetchall()
                for event in events:
                    if event.get('event_date'):
                        event['event_date'] = event['event_date'].isoformat()
                    if event.get('event_time'):
                        event['event_time'] = str(event['event_time'])
                print(f"âœ“ Returning {len(events)} events")
                return jsonify({"success": True, "data": events})
    except Exception as e:
        print(f"âŒ Error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": "Database error"}), 500


@app.route("/api/events/book", methods=["POST"])
def book_event():
    """Book event with optional ride"""
    try:
        data = request.get_json()
        print(f"ðŸ“ Event booking: {data}")

        required_fields = ["user_id", "event_id", "num_tickets"]
        if not data or not all(k in data for k in required_fields):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        user_id = data["user_id"]
        event_id = data["event_id"]
        num_tickets = data.get("num_tickets", 1)
        with_ride = data.get("with_ride", False)
        pickup_location = data.get("pickup_location", "")

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Verify user exists
                cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
                if not cur.fetchone():
                    return jsonify({"success": False, "error": "User not found"}), 404

                # Get event info
                cur.execute("SELECT price, available_seats, location FROM events WHERE id = %s", (event_id,))
                event_info = cur.fetchone()
                if not event_info:
                    return jsonify({"success": False, "error": "Event not found"}), 404

                price, available_seats, event_location = event_info

                if available_seats < num_tickets:
                    return jsonify({"success": False, "error": "Not enough seats"}), 400

                total_amount = float(price) * num_tickets

                # Create event booking
                ride_status = 'scheduled' if with_ride else 'no_ride'

                cur.execute("""
                    INSERT INTO event_bookings 
                    (user_id, event_id, num_tickets, total_amount, status, 
                     with_ride, pickup_location, ride_status)
                    VALUES (%s, %s, %s, %s, 'confirmed', %s, %s, %s) 
                    RETURNING id
                """, (user_id, event_id, num_tickets, total_amount, with_ride, pickup_location, ride_status))

                booking_id = cur.fetchone()[0]

                # Update available seats
                cur.execute("UPDATE events SET available_seats = available_seats - %s WHERE id = %s",
                            (num_tickets, event_id))

                # If with ride, create the TO event ride
                to_ride_id = None
                if with_ride and pickup_location:
                    fare = calculate_fare(pickup_location, event_location)
                    cur.execute("""
                        INSERT INTO rides 
                        (user_id, source_location, dest_location, status, fare, 
                         ride_type, event_booking_id)
                        VALUES (%s, %s, %s, 'requested', %s, 'event_to', %s)

                        RETURNING id
                    """, (user_id, pickup_location, event_location, fare, booking_id))

                    to_ride_id = cur.fetchone()[0]

                    # Update booking with ride ID
                    cur.execute("""
                        UPDATE event_bookings 
                        SET to_event_ride_id = %s 
                        WHERE id = %s
                    """, (to_ride_id, booking_id))

                    print(f"âœ“ Created TO event ride {to_ride_id}")

                print(f"âœ“ Event booking {booking_id} created (with_ride={with_ride})")

                return jsonify({
                    "success": True,
                    "booking_id": booking_id,
                    "total_amount": total_amount,
                    "with_ride": with_ride,
                    "to_ride_id": to_ride_id,
                    "message": f"Successfully booked {num_tickets} ticket(s)!" +
                               (" Ride scheduled!" if with_ride else "")
                }), 201

    except Exception as e:
        print(f"âŒ Error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/users/<int:user_id>/event-bookings", methods=["GET"])
def get_user_event_bookings(user_id):
    """Get user's event bookings with ride info"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT 
                        eb.*,
                        e.title as event_title, 
                        e.event_date, 
                        e.event_time, 
                        e.location as event_location, 
                        e.image_emoji,
                        r1.id as to_ride_id,
                        r1.status as to_ride_status,
                        r1.driver_id as to_ride_driver_id,
                        r2.id as from_ride_id,
                        r2.status as from_ride_status,
                        r2.driver_id as from_ride_driver_id
                    FROM event_bookings eb
                    JOIN events e ON eb.event_id = e.id
                    LEFT JOIN rides r1 ON eb.to_event_ride_id = r1.id
                    LEFT JOIN rides r2 ON eb.from_event_ride_id = r2.id
                    WHERE eb.user_id = %s 
                    ORDER BY e.event_date DESC
                """, (user_id,))
                bookings = cur.fetchall()

                for b in bookings:
                    if b.get('booking_date'):
                        b['booking_date'] = b['booking_date'].isoformat()
                    if b.get('event_date'):
                        b['event_date'] = b['event_date'].isoformat()
                    if b.get('event_time'):
                        b['event_time'] = str(b['event_time'])

                return jsonify({"success": True, "data": bookings})
    except Exception as e:
        print(f"âŒ Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/event-bookings/<int:booking_id>/start-ride", methods=["POST"])
def start_event_ride(booking_id):
    """Start the ride to event"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Get booking and ride info
                cur.execute("""
                    SELECT eb.to_event_ride_id, eb.ride_status, r.status
                    FROM event_bookings eb
                    LEFT JOIN rides r ON eb.to_event_ride_id = r.id
                    WHERE eb.id = %s
                """, (booking_id,))

                result = cur.fetchone()
                if not result:
                    return jsonify({"success": False, "error": "Booking not found"}), 404

                ride_id, ride_status, ride_db_status = result

                if not ride_id:
                    return jsonify({"success": False, "error": "No ride scheduled"}), 400

                # Update ride status to requested
                cur.execute("""
                    UPDATE rides 
                    SET status = 'requested' 
                    WHERE id = %s
                """, (ride_id,))

                # Update booking ride status
                cur.execute("""
                    UPDATE event_bookings 
                    SET ride_status = 'to_event' 
                    WHERE id = %s
                """, (booking_id,))

                print(f"âœ“ Started ride {ride_id} to event (booking {booking_id})")

                return jsonify({
                    "success": True,
                    "message": "Ride started! Waiting for driver...",
                    "ride_id": ride_id
                })

    except Exception as e:
        print(f"âŒ Error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500



@app.route("/api/event-bookings/<int:booking_id>/mark-complete", methods=["POST"])
def mark_event_complete(booking_id):
    """Mark event as complete and create return ride"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Get booking info
                cur.execute("""
                    SELECT 
                        eb.user_id, 
                        eb.pickup_location, 
                        e.location as event_location,
                        eb.from_event_ride_id
                    FROM event_bookings eb
                    JOIN events e ON eb.event_id = e.id
                    WHERE eb.id = %s
                """, (booking_id,))

                result = cur.fetchone()
                if not result:
                    return jsonify({"success": False, "error": "Booking not found"}), 404

                user_id, pickup_location, event_location, existing_from_ride = result

                # If return ride already exists, just activate it
                if existing_from_ride:
                    cur.execute("UPDATE rides SET status = 'waiting' WHERE id = %s", (existing_from_ride,))
                    from_ride_id = existing_from_ride
                else:
                    # Create return ride
                    fare = calculate_fare(event_location, pickup_location)
                    cur.execute("""
                        INSERT INTO rides 
                        (user_id, source_location, dest_location, status, fare, 
                         ride_type, event_booking_id)
                        VALUES (%s, %s, %s, 'waiting', %s, 'event_from', %s)
                        RETURNING id
                    """, (user_id, event_location, pickup_location, fare, booking_id))

                    from_ride_id = cur.fetchone()[0]

                    # Update booking with return ride ID
                    cur.execute("""
                        UPDATE event_bookings 
                        SET from_event_ride_id = %s 
                        WHERE id = %s
                    """, (from_ride_id, booking_id))

                # Update ride status
                cur.execute("""
                    UPDATE event_bookings 
                    SET ride_status = 'from_event' 
                    WHERE id = %s
                """, (booking_id,))

                print(f"âœ“ Event completed! Return ride {from_ride_id} created")

                return jsonify({
                    "success": True,
                    "message": "Return ride scheduled! Waiting for driver...",
                    "from_ride_id": from_ride_id
                })

    except Exception as e:
        print(f"âŒ Error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# --- Health check endpoint (added) ---
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Returns JSON health status and checks DB connectivity.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM rides;")
                cnt = cur.fetchone()[0]
        return jsonify({'service': 'Core Server API', 'status': 'running', 'rides_count': cnt}), 200
    except Exception as e:
        return jsonify({'service': 'Core Server API', 'status': 'db_error', 'details': str(e)}), 500

# ============= END ENHANCED EVENT ENDPOINTS =============



# --- User & Driver Registration Endpoints (added) ---
@app.route('/api/users/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['name', 'email', 'phone']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (name, email, phone, created_at) VALUES (%s, %s, %s, NOW()) RETURNING id;",
                    (data['name'], data['email'], data['phone'])
                )
                res = cur.fetchone()
                if res:
                    user_id = res[0]
                else:
                    return jsonify({'success': False, 'error': 'Failed to create user'}), 500

        return jsonify({'success': True, 'user_id': user_id}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500

@app.route('/api/drivers/register', methods=['POST'])
def register_driver():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['name', 'email', 'vehicle_details']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO drivers (name, email, vehicle_details, online_status, created_at) VALUES (%s, %s, %s, 'offline', NOW()) RETURNING id;",
                    (data['name'], data['email'], data['vehicle_details'])
                )
                res = cur.fetchone()
                if res:
                    driver_id = res[0]
                else:
                    return jsonify({'success': False, 'error': 'Failed to create driver'}), 500

        return jsonify({'success': True, 'driver_id': driver_id}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500
    
# ================= DRIVER COMPLETED RIDES ENDPOINT =================

@app.route('/api/drivers/<int:driver_id>/completed-rides', methods=['GET'])
def get_completed_rides(driver_id):
    """
    Returns all completed rides for a driver + earnings summary.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:

                # Fetch completed rides
                cur.execute("""
                    SELECT id, user_id, fare, completed_at
                    FROM rides
                    WHERE driver_id = %s AND status = 'completed'
                    ORDER BY completed_at DESC;
                """, (driver_id,))
                rides = cur.fetchall()

                # Calculate totals
                total_rides = len(rides)
                total_earnings = sum(r['fare'] for r in rides) if rides else 0.0

                return jsonify({
                    "success": True,
                    "driver_id": driver_id,
                    "total_rides": total_rides,
                    "total_earnings": total_earnings,
                    "data": rides
                }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "internal_server_error",
            "details": str(e)
        }), 500


if __name__ == '__main__':
    print('=' * 60)
    print('ðŸš— Mini Uber Core Server')
    print('=' * 60)
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    print(f'Server starting at: http://localhost:{port}')
    print('Queue system: First-In-First-Out (FIFO)')
    print('Real-time updates: Enabled')
    print('=' * 60)
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)

# --- Driver Completed Rides (today) / Earnings ---
@app.route('/api/drivers/<int:driver_id>/completed-rides', methods=['GET'])
def get_completed_rides_today(driver_id):
    """
    Returns completed rides for the driver today and a summary (total rides, total earnings).
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT id, user_id, fare, created_at, started_at, completed_at
                    FROM rides
                    WHERE driver_id = %s
                      AND status = 'completed'
                      AND completed_at >= date_trunc('day', NOW())
                    ORDER BY completed_at DESC;
                    """,
                    (driver_id,)
                )
                rides = cur.fetchall()

                total_earnings = sum((r.get('fare') or 0) for r in rides)
                for r in rides:
                    if r.get('created_at'):
                        r['created_at'] = r['created_at'].isoformat()
                    if r.get('started_at'):
                        r['started_at'] = r['started_at'].isoformat()
                    if r.get('completed_at'):
                        r['completed_at'] = r['completed_at'].isoformat()

        return jsonify({
            'success': True,
            'summary': {
                'total_rides': len(rides),
                'total_earnings': float(total_earnings)
            },
            'data': rides
        }), 200

    except Exception as e:
        print("ERROR in get_completed_rides_today:", e)
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'internal_server_error', 'details': str(e)}), 500
