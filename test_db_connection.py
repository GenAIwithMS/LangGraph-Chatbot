"""
Quick Database Connection Test
Run this to verify your MySQL connection is working
"""
import sys
from database.config import DatabaseConfig


def test_connection():
    """Test MySQL connection with current configuration"""
    try:
        from sqlalchemy import inspect
        from sqlalchemy.exc import SQLAlchemyError
        
        print("=" * 60)
        print("MySQL Connection Test (SQLAlchemy)")
        print("=" * 60)
        
        print(f"\n📊 Testing connection with:")
        print(f"  Host: {DatabaseConfig.HOST}:{DatabaseConfig.PORT}")
        print(f"  User: {DatabaseConfig.USER}")
        print(f"  Database: {DatabaseConfig.DATABASE}")
        
        engine = DatabaseConfig.get_engine()
        
        with engine.connect() as connection:
            # Get MySQL version
            result = connection.execute(text("SELECT VERSION()"))
            version = result.scalar()
            print(f"\n✅ Successfully connected to MySQL Server")
            print(f"  MySQL Version: {version}")
            
            result = connection.execute(text("SELECT DATABASE()"))
            database = result.scalar()
            print(f"  Current Database: {database}")
            
            # Test querying tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"\n📋 Tables found ({len(tables)}):")
                for table in tables:
                    print(f"  • {table}")
            else:
                print(f"\n⚠️  No tables found. Run: python -m database.init_db")
            
            print("\n" + "=" * 60)
            print("✅ Connection test PASSED")
            print("=" * 60)
            return True
            
    except SQLAlchemyError as e:
        print(f"\n❌ Connection test FAILED")
        print(f"Error: {e}")
        print("\n💡 Troubleshooting:")
        print("  1. Verify MySQL is running")
        print("  2. Check credentials in .env file")
        print("  3. Ensure database exists (run: python -m database.init_db)")
        print("=" * 60)
        return False
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    from sqlalchemy import text
    success = test_connection()
    sys.exit(0 if success else 1)
