import psycopg
from psycopg import sql
import sys

DB_NAME = "miniuberdb"
DB_USER = "postgres"
DB_PASS = "Samehada@1234"
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database():
    try:
        conn = psycopg.connect(f"user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT} dbname=postgres", autocommit=True)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        if not cur.fetchone():
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"✓ Database {DB_NAME} created!")
        else:
            print(f"✓ Database {DB_NAME} exists")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def get_db_connection():
    return psycopg.connect(f"user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT} dbname={DB_NAME}", autocommit=True)

def setup_schema_and_data():
    drop_commands = [
        "DROP TABLE IF EXISTS event_bookings CASCADE",
        "DROP TABLE IF EXISTS events CASCADE",
        "DROP TABLE IF EXISTS rides CASCADE",
        "DROP TABLE IF EXISTS users CASCADE",
        "DROP TABLE IF EXISTS drivers CASCADE"
    ]

    create_commands = [
        """CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL, email VARCHAR(100) UNIQUE NOT NULL, phone VARCHAR(20), created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)""",
        """CREATE TABLE drivers (id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL, email VARCHAR(100) UNIQUE NOT NULL, vehicle_details VARCHAR(255), online_status VARCHAR(20) DEFAULT 'offline', created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)""",
        """CREATE TABLE rides (id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), driver_id INTEGER REFERENCES drivers(id), source_location VARCHAR(255) NOT NULL, dest_location VARCHAR(255) NOT NULL, status VARCHAR(50) NOT NULL, fare NUMERIC(10, 2), ride_type VARCHAR(20) DEFAULT 'regular', event_booking_id INTEGER, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, completed_at TIMESTAMP WITH TIME ZONE)""",
        """CREATE TABLE events (id SERIAL PRIMARY KEY, title VARCHAR(200) NOT NULL, description TEXT, event_date DATE NOT NULL, event_time TIME, location VARCHAR(255) NOT NULL, category VARCHAR(50), price NUMERIC(10, 2) DEFAULT 0, image_emoji VARCHAR(10), available_seats INTEGER DEFAULT 100, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)""",
        """CREATE TABLE event_bookings (id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), event_id INTEGER NOT NULL REFERENCES events(id), booking_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, num_tickets INTEGER DEFAULT 1, total_amount NUMERIC(10, 2), status VARCHAR(20) DEFAULT 'confirmed', with_ride BOOLEAN DEFAULT FALSE, pickup_location VARCHAR(255), ride_status VARCHAR(30) DEFAULT 'no_ride', to_event_ride_id INTEGER, from_event_ride_id INTEGER)""",
        # --- NEW TABLE FOR SKIPS ---
        """CREATE TABLE ride_skips (ride_id INTEGER REFERENCES rides(id), driver_id INTEGER REFERENCES drivers(id), skipped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (ride_id, driver_id))"""
    ]

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for cmd in drop_commands:
                    cur.execute(cmd)
                print("✓ Tables dropped")
                for cmd in create_commands:
                    cur.execute(cmd)
                print("✓ Tables created with EVENT-RIDE integration")

                # Sample data
                cur.execute("INSERT INTO users (id, name, email, phone) VALUES (%s, %s, %s, %s)", (101, 'Rohan Sharma', 'rohan@example.com', '555-0101'))
                cur.execute("INSERT INTO users (id, name, email, phone) VALUES (%s, %s, %s, %s)", (102, 'Anjali Verma', 'anjali@example.com', '555-0102'))
                cur.execute("INSERT INTO drivers (id, name, email, vehicle_details) VALUES (%s, %s, %s, %s)", (201, 'Priya Singh', 'priya@example.com', 'Maruti Swift'))
                cur.execute("INSERT INTO drivers (id, name, email, vehicle_details) VALUES (%s, %s, %s, %s)", (202, 'Raj Kumar', 'raj@example.com', 'Honda City'))

                events = [
                    ('Sunburn Music Festival', "India's biggest EDM festival", '2025-12-28', '18:00', 'Vagator Beach, Goa', 'Music', 2500, '🎵', 5000),
                    ('TechCrunch Bangalore 2025', 'Startup conference', '2025-12-15', '09:00', 'KTPO Convention Centre, Bangalore', 'Technology', 1500, '💻', 800),
                    ('Stand-up Comedy Night', "Top comedians", '2025-11-30', '20:00', 'Phoenix Marketcity, Bangalore', 'Comedy', 500, '😂', 200),
                    ('Cricket: India vs Australia', 'T20 Match', '2025-12-10', '19:30', 'M. Chinnaswamy Stadium', 'Sports', 1200, '🏏', 35000),
                    ('Food Truck Festival', '50+ food trucks', '2025-11-25', '12:00', 'Cubbon Park, Bangalore', 'Food', 0, '🍔', 2000),
                    ('Diwali Mela 2025', 'Festival celebration', '2025-11-12', '17:00', 'Lalbagh Garden', 'Festival', 100, '🪔', 3000),
                    ('Art Exhibition', 'Modern art showcase', '2025-12-05', '10:00', 'National Gallery, Bangalore', 'Art', 200, '🎨', 500),
                    ('Yoga Retreat', 'Wellness weekend', '2025-12-20', '06:00', 'Nandi Hills', 'Wellness', 3000, '🧘', 50)
                ]

                for e in events:
                    cur.execute("INSERT INTO events (title, description, event_date, event_time, location, category, price, image_emoji, available_seats) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", e)

                print("✓ Sample data inserted (8 events)")

                cur.execute("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users))")
                cur.execute("SELECT setval('drivers_id_seq', (SELECT MAX(id) FROM drivers))")
                cur.execute("SELECT setval('rides_id_seq', 1, false)")
                cur.execute("SELECT setval('events_id_seq', (SELECT MAX(id) FROM events))")
                cur.execute("SELECT setval('event_bookings_id_seq', 1, false)")
                print("✓ Sequences reset")
                print("\n✅ Database ready with EVENT-RIDE integration!")
                return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("RAAHI - Enhanced Database (Events + Rides)")
    print("="*60)
    if create_database() and setup_schema_and_data():
        print("="*60)
        print("✅ Enhanced database completed!")
        print("="*60)
    else:
        sys.exit("✗ Failed")

if __name__ == "__main__":
    main()
