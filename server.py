from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import psycopg
from psycopg.rows import dict_row
import os

app = Flask(__name__)
CORS(app)

# Database Configuration
DB_NAME = "mini_uber_db"
DB_USER = "postgres"
DB_PASS = "Laksh@2004"
DB_HOST = "localhost"
DB_PORT = "5432"

def get_db_connection():
    """Establishes a connection to the PostgreSQL database using psycopg3."""
    try:
        # psycopg3 connection string format
        conn = psycopg.connect(
            f"user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT} dbname={DB_NAME}"
        )
        return conn
    except psycopg.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        raise

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM rides;")
        ride_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        db_status = f"Connected - {ride_count} rides in system"
    except Exception as e:
        db_status = f"Connection failed: {str(e)}"
    
    return jsonify({
        'service': 'Core Server API (psycopg3)',
        'status': 'running',
        'database': db_status,
        'timestamp': datetime.now().isoformat(),
        'port': 3000
    })

# ===== USER ENDPOINTS =====
@app.route('/api/users/rides', methods=['POST'])
def create_ride_request():
    """Create a new ride request from user"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    user_id = data.get('user_id')
    source_location = data.get('source_location')
    dest_location = data.get('dest_location')
    ride_type = data.get('ride_type', 'standard')  # standard, premium, shared

    if not all([user_id, source_location, dest_location]):
        return jsonify({
            'error': 'Missing required fields: user_id, source_location, dest_location'
        }), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """INSERT INTO rides (user_id, source_location, dest_location, ride_type, status) 
               VALUES (%s, %s, %s, %s, %s) RETURNING id, created_at;""",
            (int(user_id), source_location, dest_location, ride_type, 'requested')
        )
        
        ride_id, created_at = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        new_ride = {
            'id': ride_id,
            'user_id': int(user_id),
            'source_location': source_location,
            'dest_location': dest_location,
            'ride_type': ride_type,
            'status': 'requested',
            'created_at': created_at.isoformat()
        }
        
        print(f'✅ User ride request created: Ride #{ride_id}')
        return jsonify({
            'success': True,
            'message': 'Ride request created successfully',
            'data': new_ride
        }), 201

    except Exception as e:
        print(f"❌ Error creating ride: {e}")
        return jsonify({'error': 'Failed to create ride request', 'details': str(e)}), 500

@app.route('/api/users/<int:user_id>/rides', methods=['GET'])
def get_user_rides(user_id):
    """Get all rides for a specific user"""
    try:
        conn = get_db_connection()
        # Use dict_row factory for dictionary-like access
        cur = conn.cursor(row_factory=dict_row)
        cur.execute(
            "SELECT * FROM rides WHERE user_id = %s ORDER BY created_at DESC;", 
            (user_id,)
        )
        rides = cur.fetchall()
        cur.close()
        conn.close()

        # Convert datetime objects to ISO format
        for ride in rides:
            if ride['created_at']:
                ride['created_at'] = ride['created_at'].isoformat()
            if ride.get('updated_at'):
                ride['updated_at'] = ride['updated_at'].isoformat()

        return jsonify({
            'success': True,
            'user_id': user_id,
            'data': rides
        })
    except Exception as e:
        print(f"❌ Error fetching user rides: {e}")
        return jsonify({'error': 'Failed to fetch rides', 'details': str(e)}), 500

# ===== DRIVER ENDPOINTS =====
@app.route('/api/drivers/rides/available', methods=['GET'])
def get_available_rides():
    """Get all rides available for drivers to accept"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        cur.execute(
            "SELECT * FROM rides WHERE status IN ('requested', 'pending') ORDER BY created_at ASC;"
        )
        rides = cur.fetchall()
        cur.close()
        conn.close()

        # Convert datetime objects
        for ride in rides:
            if ride['created_at']:
                ride['created_at'] = ride['created_at'].isoformat()
            if ride.get('updated_at'):
                ride['updated_at'] = ride['updated_at'].isoformat()

        return jsonify({
            'success': True,
            'message': f'Found {len(rides)} available rides',
            'data': rides
        })
    except Exception as e:
        print(f"❌ Error fetching available rides: {e}")
        return jsonify({'error': 'Failed to fetch available rides', 'details': str(e)}), 500

@app.route('/api/drivers/rides/<int:ride_id>/accept', methods=['PUT'])
def accept_ride(ride_id):
    """Driver accepts a ride"""
    data = request.get_json()
    driver_id = data.get('driver_id') if data else None
    
    if not driver_id:
        return jsonify({'error': 'driver_id is required'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        
        # Check if ride exists and is available
        cur.execute("SELECT * FROM rides WHERE id = %s;", (ride_id,))
        ride = cur.fetchone()
        
        if not ride:
            return jsonify({'error': 'Ride not found'}), 404
            
        if ride['status'] not in ['requested', 'pending']:
            return jsonify({'error': 'Ride is not available for acceptance'}), 400

        # Update ride with driver info
        cur.execute(
            """UPDATE rides SET driver_id = %s, status = %s, updated_at = CURRENT_TIMESTAMP 
               WHERE id = %s RETURNING *;""",
            (int(driver_id), 'accepted', ride_id)
        )
        
        updated_ride = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        # Convert datetime objects
        if updated_ride['created_at']:
            updated_ride['created_at'] = updated_ride['created_at'].isoformat()
        if updated_ride['updated_at']:
            updated_ride['updated_at'] = updated_ride['updated_at'].isoformat()

        print(f'✅ Driver {driver_id} accepted ride #{ride_id}')
        return jsonify({
            'success': True,
            'message': 'Ride accepted successfully',
            'data': updated_ride
        })

    except Exception as e:
        print(f"❌ Error accepting ride: {e}")
        return jsonify({'error': 'Failed to accept ride', 'details': str(e)}), 500

@app.route('/api/drivers/<int:driver_id>/rides', methods=['GET'])
def get_driver_rides(driver_id):
    """Get all rides assigned to a specific driver"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        cur.execute(
            "SELECT * FROM rides WHERE driver_id = %s ORDER BY created_at DESC;", 
            (driver_id,)
        )
        rides = cur.fetchall()
        cur.close()
        conn.close()

        # Convert datetime objects
        for ride in rides:
            if ride['created_at']:
                ride['created_at'] = ride['created_at'].isoformat()
            if ride.get('updated_at'):
                ride['updated_at'] = ride['updated_at'].isoformat()

        return jsonify({
            'success': True,
            'driver_id': driver_id,
            'data': rides
        })
    except Exception as e:
        print(f"❌ Error fetching driver rides: {e}")
        return jsonify({'error': 'Failed to fetch driver rides', 'details': str(e)}), 500

@app.route('/api/drivers/rides/<int:ride_id>/status', methods=['PUT'])
def update_ride_status(ride_id):
    """Update ride status (start trip, complete trip, etc.)"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    new_status = data.get('status')
    driver_id = data.get('driver_id')
    
    valid_statuses = ['accepted', 'in_progress', 'completed', 'cancelled']
    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        
        # Verify driver owns this ride
        cur.execute("SELECT * FROM rides WHERE id = %s AND driver_id = %s;", (ride_id, driver_id))
        ride = cur.fetchone()
        
        if not ride:
            return jsonify({'error': 'Ride not found or not assigned to this driver'}), 404

        # Update status
        cur.execute(
            "UPDATE rides SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *;",
            (new_status, ride_id)
        )
        
        updated_ride = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        # Convert datetime objects
        if updated_ride['created_at']:
            updated_ride['created_at'] = updated_ride['created_at'].isoformat()
        if updated_ride['updated_at']:
            updated_ride['updated_at'] = updated_ride['updated_at'].isoformat()

        print(f'✅ Ride #{ride_id} status updated to: {new_status}')
        return jsonify({
            'success': True,
            'message': f'Ride status updated to {new_status}',
            'data': updated_ride
        })

    except Exception as e:
        print(f"❌ Error updating ride status: {e}")
        return jsonify({'error': 'Failed to update ride status', 'details': str(e)}), 500
    
    # Add this new endpoint to your server.py file

@app.route('/api/rides/<int:ride_id>/cancel', methods=['PUT'])
def cancel_ride(ride_id):
    """
    Allows a user or driver to cancel a ride.
    """
    try:
        data = request.get_json()
        cancelled_by = data.get('cancelled_by', 'system') # Can be 'user' or 'driver'

        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)

        # First, check the current status of the ride
        cur.execute("SELECT status FROM rides WHERE id = %s;", (ride_id,))
        ride = cur.fetchone()

        if not ride:
            return jsonify({'error': 'Ride not found'}), 404
        
        # Prevent cancellation if the ride is already completed or cancelled
        if ride['status'] in ['completed', 'cancelled']:
            return jsonify({
                'error': 'Cannot cancel ride',
                'details': f'Ride is already {ride["status"]}.'
            }), 400

        # Update the ride status to 'cancelled'
        cur.execute("""
            UPDATE rides 
            SET status = 'cancelled', cancelled_by = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s 
            RETURNING *;
        """, (cancelled_by, ride_id))
        
        updated_ride = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        print(f"✅ Ride #{ride_id} was cancelled by {cancelled_by}")
        
        return jsonify({
            'success': True,
            'message': 'Ride has been successfully cancelled.',
            'data': {
                'id': updated_ride['id'],
                'status': updated_ride['status'],
                'cancelled_by': updated_ride['cancelled_by']
            }
        })

    except Exception as e:
        print(f"❌ Error cancelling ride: {e}")
        return jsonify({'error': 'Failed to cancel ride', 'details': str(e)}), 500

# ===== ADMIN ENDPOINTS =====
@app.route('/api/admin/rides', methods=['GET'])
def get_all_rides():
    """Get all rides in the system (admin view)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)
        cur.execute("SELECT * FROM rides ORDER BY created_at DESC;")
        rides = cur.fetchall()
        cur.close()
        conn.close()

        # Convert datetime objects
        for ride in rides:
            if ride['created_at']:
                ride['created_at'] = ride['created_at'].isoformat()
            if ride.get('updated_at'):
                ride['updated_at'] = ride['updated_at'].isoformat()

        return jsonify({
            'success': True,
            'total_rides': len(rides),
            'data': rides
        })
    except Exception as e:
        print(f"❌ Error fetching all rides: {e}")
        return jsonify({'error': 'Failed to fetch rides', 'details': str(e)}), 500

if __name__ == '__main__':
    print('🚗 Mini Uber Core Server API starting (psycopg3)...')
    print('📡 Endpoints available at: http://localhost:3000')
    print('👥 User endpoints: /api/users/*')
    print('🚕 Driver endpoints: /api/drivers/*') 
    print('🔧 Admin endpoints: /api/admin/*')
    print('🏥 Health check: /api/health')
    app.run(host='0.0.0.0', port=3000, debug=True)