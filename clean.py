import psycopg
from psycopg import sql
import sys

# Database configuration
DB_NAME = "mini_uber_db"
DB_USER = "postgres"
DB_PASS = "Laksh@2004"
DB_HOST = "localhost"
DB_PORT = "5432"

def setup_schema():
    """Drops old tables and creates a fresh schema."""
    conn_string = f"user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT} dbname={DB_NAME}"
    
    drop_commands = [
        "DROP TABLE IF EXISTS rides CASCADE;",
        "DROP TABLE IF EXISTS users CASCADE;",
        "DROP TABLE IF EXISTS drivers CASCADE;"
    ]

    create_commands = [
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE drivers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            vehicle_details VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE rides (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            driver_id INTEGER REFERENCES drivers(id),
            source_location VARCHAR(255) NOT NULL,
            dest_location VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        );
        """
    ]

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                print("🗑️  Dropping old tables...")
                for command in drop_commands:
                    cur.execute(command)

                print("🛠️  Creating new, clean tables...")
                for command in create_commands:
                    cur.execute(command)
        print("✅ Schema created successfully. No sample data was added.")
        return True
    except Exception as e:
        print(f"❌ Error during schema setup: {e}")
        return False

def main():
    print("🚗 Mini Uber Clean Database Setup")
    print("=" * 50)
    # Simplified main function, assumes database exists
    if not setup_schema():
        sys.exit(1)
    print("\n🎉 Database is clean and ready for registrations!")

if __name__ == '__main__':
    main()
