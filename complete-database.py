import psycopg
from psycopg import sql
import sys

# Database configuration - UPDATE YOUR PASSWORD HERE!
DB_NAME = "mini_uber_db"
DB_USER = "postgres"
DB_PASS = "Samehada@1234"  # ⚠️ CHANGE THIS TO YOUR POSTGRESQL PASSWORD
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database():
    """Create the database if it doesn't exist"""
    try:
        print("🔌 Connecting to PostgreSQL server...")
        # Note: psycopg3 uses different connection syntax
        conn = psycopg.connect(
            f"user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT} dbname=postgres",
            autocommit=True
        )
        
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cur.fetchone()
        
        if exists:
            print(f"✅ Database '{DB_NAME}' already exists")
        else:
            # Use sql.Identifier for safe database name handling
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"✅ Database '{DB_NAME}' created successfully")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_tables_and_data():
    """Create all tables with enhanced schema and sample data"""
    try:
        print(f"🔌 Connecting to database '{DB_NAME}'...")
        # psycopg3 connection string format
        conn = psycopg.connect(
            f"user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT} dbname={DB_NAME}"
        )
        
        cur = conn.cursor()
        
        print("📋 Creating enhanced rides table...")
        # Enhanced rides table with all new columns
        create_rides_table = """
        CREATE TABLE IF NOT EXISTS rides (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            driver_id INTEGER NULL,
            source_location VARCHAR(255) NOT NULL,
            dest_location VARCHAR(255) NOT NULL,
            ride_type VARCHAR(50) DEFAULT 'standard',
            status VARCHAR(50) DEFAULT 'requested',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            estimated_fare DECIMAL(10,2) NULL,
            actual_fare DECIMAL(10,2) NULL,
            distance_km DECIMAL(6,2) NULL,
            duration_minutes INTEGER NULL,
            cancelled_by VARCHAR(20) NULL,
            cancellation_reason TEXT NULL
        );
        """
        cur.execute(create_rides_table)
        
        print("🔍 Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_rides_user_id ON rides(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_rides_driver_id ON rides(driver_id);",
            "CREATE INDEX IF NOT EXISTS idx_rides_status ON rides(status);",
            "CREATE INDEX IF NOT EXISTS idx_rides_created_at ON rides(created_at);"
        ]
        for index in indexes:
            cur.execute(index)
        
        print("⏰ Creating trigger for updated_at...")
        # Create trigger for auto-updating updated_at
        trigger_function = """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
        cur.execute(trigger_function)
        
        trigger = """
        DROP TRIGGER IF EXISTS update_rides_updated_at ON rides;
        CREATE TRIGGER update_rides_updated_at 
            BEFORE UPDATE ON rides 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
        cur.execute(trigger)
        
        print("👥 Creating users table...")
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        cur.execute(create_users_table)
        
        print("🚕 Creating drivers table...")
        create_drivers_table = """
        CREATE TABLE IF NOT EXISTS drivers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20),
            license_number VARCHAR(50),
            vehicle_type VARCHAR(50),
            vehicle_plate VARCHAR(20),
            status VARCHAR(20) DEFAULT 'offline',
            rating DECIMAL(3,2) DEFAULT 5.00,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        cur.execute(create_drivers_table)
        
        print("📝 Inserting sample data...")
        
        # Insert sample users
        insert_users = """
        INSERT INTO users (id, name, email, phone) VALUES
        (123, 'John Doe', 'john.doe@email.com', '+1234567890'),
        (124, 'Jane Smith', 'jane.smith@email.com', '+1234567891'),
        (125, 'Mike Johnson', 'mike.johnson@email.com', '+1234567892')
        ON CONFLICT (email) DO NOTHING;
        """
        cur.execute(insert_users)
        
        # Insert sample drivers
        insert_drivers = """
        INSERT INTO drivers (id, name, email, phone, license_number, vehicle_type, vehicle_plate, status) VALUES
        (456, 'Driver Alex', 'alex.driver@email.com', '+1234567800', 'DL123456', 'Sedan', 'ABC-123', 'available'),
        (457, 'Driver Sarah', 'sarah.driver@email.com', '+1234567801', 'DL123457', 'SUV', 'XYZ-789', 'available'),
        (458, 'Driver Tom', 'tom.driver@email.com', '+1234567802', 'DL123458', 'Hatchback', 'PQR-456', 'busy')
        ON CONFLICT (email) DO NOTHING;
        """
        cur.execute(insert_drivers)
        
        # Insert sample rides
        insert_rides = """
        INSERT INTO rides (user_id, driver_id, source_location, dest_location, ride_type, status, estimated_fare) VALUES
        (123, NULL, 'Airport Terminal 1', 'Downtown Hotel', 'standard', 'requested', 25.50),
        (123, 456, 'Home', 'Office Complex', 'premium', 'accepted', 18.75),
        (124, 456, 'Shopping Mall', 'Restaurant District', 'standard', 'in_progress', 12.30),
        (124, 457, 'University Campus', 'City Library', 'shared', 'completed', 8.90),
        (125, NULL, 'Train Station', 'Business Park', 'standard', 'requested', 22.10),
        (125, NULL, 'Coffee Shop', 'Movie Theater', 'premium', 'requested', 15.60)
        ON CONFLICT DO NOTHING;
        """
        cur.execute(insert_rides)
        
        # Commit all changes
        conn.commit()
        
        # Verify data
        cur.execute("SELECT COUNT(*) FROM rides;")
        rides_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM users;")
        users_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM drivers;")
        drivers_count = cur.fetchone()[0]
        
        print(f"✅ Tables created successfully!")
        print(f"   📊 Rides: {rides_count} records")
        print(f"   👥 Users: {users_count} records")
        print(f"   🚕 Drivers: {drivers_count} records")
        
        # Show sample data
        print("\n📋 Sample rides:")
        cur.execute("SELECT id, user_id, driver_id, source_location, dest_location, status FROM rides LIMIT 3;")
        rides = cur.fetchall()
        for ride in rides:
            driver_info = f"Driver {ride[2]}" if ride[2] else "No driver assigned"
            print(f"   🚗 Ride #{ride[0]}: User {ride[1]} | {ride[3]} → {ride[4]} | {ride[5]} | {driver_info}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def test_all_operations():
    """Test all database operations that the server will use"""
    try:
        print("\n🧪 Testing database operations...")
        conn = psycopg.connect(
            f"user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT} dbname={DB_NAME}"
        )
        
        cur = conn.cursor()
        
        # Test 1: Get available rides (what drivers see)
        cur.execute("SELECT COUNT(*) FROM rides WHERE status IN ('requested', 'pending');")
        available_count = cur.fetchone()[0]
        print(f"✅ Available rides for drivers: {available_count}")
        
        # Test 2: Get user rides
        cur.execute("SELECT COUNT(*) FROM rides WHERE user_id = 123;")
        user_rides = cur.fetchone()[0]
        print(f"✅ Rides for user 123: {user_rides}")
        
        # Test 3: Get driver rides
        cur.execute("SELECT COUNT(*) FROM rides WHERE driver_id = 456;")
        driver_rides = cur.fetchone()[0]
        print(f"✅ Rides for driver 456: {driver_rides}")
        
        # Test 4: Insert new ride (simulate user request)
        cur.execute("""
            INSERT INTO rides (user_id, source_location, dest_location, ride_type, status) 
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """, (999, 'Test Location A', 'Test Location B', 'standard', 'requested'))
        
        new_ride_id = cur.fetchone()[0]
        print(f"✅ Created test ride: #{new_ride_id}")
        
        # Test 5: Update ride (simulate driver accepting)
        cur.execute("""
            UPDATE rides SET driver_id = %s, status = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s RETURNING id;
        """, (999, 'accepted', new_ride_id))
        
        updated_ride = cur.fetchone()
        print(f"✅ Updated ride status: #{updated_ride[0]}")
        
        # Clean up test data
        cur.execute("DELETE FROM rides WHERE id = %s;", (new_ride_id,))
        conn.commit()
        print(f"✅ Cleaned up test ride: #{new_ride_id}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False

def main():
    print("🚗 Mini Uber Complete Database Setup (psycopg3)")
    print("=" * 50)
    
    # Step 1: Create database
    if not create_database():
        print("❌ Failed to create database. Exiting...")
        sys.exit(1)
    
    # Step 2: Create tables and insert data
    if not create_tables_and_data():
        print("❌ Failed to create tables. Exiting...")
        sys.exit(1)
    
    # Step 3: Test operations
    if not test_all_operations():
        print("❌ Database tests failed. Exiting...")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Complete database setup successful!")
    print("\n📋 What was created:")
    print("   🗄️  Database: mini_uber_db")
    print("   📊 Table: rides (with enhanced columns)")
    print("   👥 Table: users")
    print("   🚕 Table: drivers")
    print("   🔍 Indexes for performance")
    print("   ⏰ Auto-update triggers")
    print("   📝 Sample data for testing")
    
    print("\n🚀 Next steps:")
    print("1. Run: python enhanced_server.py")
    print("2. Run: python user_client.py (in another terminal)")
    print("3. Run: python driver_client.py (in another terminal)")

if __name__ == "__main__":
    main()