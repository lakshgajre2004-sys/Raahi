import psycopg
from psycopg.rows import dict_row

# Database configuration - UPDATE YOUR PASSWORD!
DB_NAME = "mini_uber_db"
DB_USER = "postgres"
DB_PASS = "Samehada@1234"  # ⚠️ CHANGE THIS
DB_HOST = "localhost"
DB_PORT = "5432"

def test_connection():
    """Test PostgreSQL connection and show data"""
    try:
        print("🔌 Testing PostgreSQL connection...")
        
        # Connect to database using psycopg3
        conn = psycopg.connect(
            f"user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT} dbname={DB_NAME}"
        )
        
        print("✅ Connected to PostgreSQL successfully!")
        
        # Test with dictionary row factory for easy data access
        cur = conn.cursor(row_factory=dict_row)
        
        # Show PostgreSQL version
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"📊 PostgreSQL Version: {version['version'][:50]}...")
        
        # Show rides data
        cur.execute("SELECT * FROM rides ORDER BY created_at DESC LIMIT 3;")
        rides = cur.fetchall()
        
        print(f"\n🚗 Found {len(rides)} sample rides:")
        for ride in rides:
            status_emoji = {
                'requested': '🔍', 'accepted': '✅', 
                'in_progress': '🚗', 'completed': '✅', 
                'cancelled': '❌'
            }.get(ride['status'], '📋')
            
            driver_info = f"Driver {ride['driver_id']}" if ride['driver_id'] else "No driver assigned"
            
            print(f"   {status_emoji} Ride #{ride['id']}: User {ride['user_id']}")
            print(f"      📍 {ride['source_location']} → {ride['dest_location']}")
            print(f"      🚕 {ride['ride_type']} | {ride['status']} | {driver_info}")
            print(f"      ⏰ {ride['created_at']}")
            print()
        
        # Test user-specific query (what user client needs)
        user_id = 123
        cur.execute("SELECT COUNT(*) as count FROM rides WHERE user_id = %s;", (user_id,))
        user_ride_count = cur.fetchone()['count']
        print(f"👥 User {user_id} has {user_ride_count} rides")
        
        # Test available rides query (what driver client needs)
        cur.execute("SELECT COUNT(*) as count FROM rides WHERE status IN ('requested', 'pending');")
        available_count = cur.fetchone()['count']
        print(f"🚕 {available_count} rides available for drivers")
        
        # Test driver-specific query
        driver_id = 456
        cur.execute("SELECT COUNT(*) as count FROM rides WHERE driver_id = %s;", (driver_id,))
        driver_ride_count = cur.fetchone()['count']
        print(f"🚗 Driver {driver_id} has {driver_ride_count} assigned rides")
        
        cur.close()
        conn.close()
        
        print("\n✅ All PostgreSQL operations working correctly!")
        print("🚀 Your database is ready for the Mini Uber application!")
        
        return True
        
    except psycopg.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check if PostgreSQL is running")
        print("2. Verify your password in the script")
        print("3. Make sure database 'mini_uber_db' exists")
        print("4. Run: python complete_database_setup.py")
        return False
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Mini Uber PostgreSQL Connection Test (psycopg3)")
    print("=" * 50)
    
    success = test_connection()
    
    if success:
        print("\n🎉 Database is ready!")
        print("\nNext steps:")
        print("1. Start server: python enhanced_server.py")
        print("2. Start user client: python user_client.py")
        print("3. Start driver client: python driver_client.py")
    else:
        print("\n❌ Please fix the database connection first")
        print("Run: python complete_database_setup.py")