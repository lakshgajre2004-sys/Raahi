from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import psycopg2
import psycopg2.extras # Needed for dictionary cursor

app = Flask(__name__)
CORS(app)

# --- Database Connection Details ---
DB_NAME = "mini_uber_db"
DB_USER = "postgres"
DB_PASS = "Laksh@2004" # <-- IMPORTANT: CHANGE THIS!
DB_HOST = "localhost"
DB_PORT = "5432"

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'Python Server is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/rides', methods=['POST'])
def submit_ride_request():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    source_location = data.get('source_location')
    dest_location = data.get('dest_location')
    user_id = data.get('user_id')

    if not source_location or not dest_location or not user_id:
        return jsonify({
            'error': 'Missing required fields: source_location, dest_location, user_id'
        }), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # SQL query to insert data, returning the new row's id and timestamp
        cur.execute(
            "INSERT INTO rides (user_id, source_location, dest_location, status) VALUES (%s, %s, %s, %s) RETURNING id, created_at;",
            (int(user_id), source_location, dest_location, 'pending')
        )
        
        # Fetch the returned values
        new_ride_id, created_at_from_db = cur.fetchone()
        
        # This is the essential "save" command
        conn.commit()
        
        cur.close()
        conn.close()

        # Create the response object
        new_ride = {
            'id': new_ride_id,
            'user_id': int(user_id),
            'source_location': source_location,
            'dest_location': dest_location,
            'status': 'pending',
            'created_at': created_at_from_db.isoformat()
        }
        
        print('\n✅ Data stored in PostgreSQL successfully!')
        print(f'   Ride Data: {new_ride}\n')

        return jsonify({
            'success': True,
            'message': 'Ride request submitted and stored in DB',
            'data': new_ride
        }), 201

    except Exception as e:
        # It's good practice to print the error to the server console for debugging
        print(f"\n❌ DATABASE ERROR: {e}\n")
        return jsonify({'error': 'Database operation failed', 'details': str(e)}), 500

@app.route('/api/rides', methods=['GET'])
def get_all_rides():
    try:
        conn = get_db_connection()
        # Use a dictionary cursor to get results as dicts instead of tuples
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
        cur.execute("SELECT * FROM rides ORDER BY created_at DESC;")
        rides_from_db = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': rides_from_db
        })
    except Exception as e:
        print(f"\n❌ DATABASE ERROR: {e}\n")
        return jsonify({'error': 'Database query failed', 'details': str(e)}), 500

@app.route('/api/rides/user/<int:user_id>', methods=['GET'])
def get_user_rides(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Use a parameterized query to prevent SQL injection
        cur.execute("SELECT * FROM rides WHERE user_id = %s ORDER BY created_at DESC;", (user_id,))
        user_rides = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': user_rides
        })
    except Exception as e:
        print(f"\n❌ DATABASE ERROR: {e}\n")
        return jsonify({'error': 'Database query failed', 'details': str(e)}), 500

if __name__ == '__main__':
    print('🚗 Mini Uber Python Server (with PostgreSQL) starting...')
    print('📡 API endpoints available at: http://localhost:3000')
    app.run(host='0.0.0.0', port=3000, debug=True)