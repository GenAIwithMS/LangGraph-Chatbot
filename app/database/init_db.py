"""Database Initialization Script"""
from sqlalchemy import create_engine, text
from app.database import DatabaseConfig
from app.database.models import Base


def init_database():
    """Initialize database and create tables"""
    try:
        # Create database
        engine = create_engine(
            f"mysql+pymysql://{DatabaseConfig.USER}:{DatabaseConfig.PASSWORD}@{DatabaseConfig.HOST}:{DatabaseConfig.PORT}",
            isolation_level="AUTOCOMMIT"
        )
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DatabaseConfig.DATABASE} CHARACTER SET utf8mb4"))
        engine.dispose()
        
        # Create tables
        Base.metadata.create_all(DatabaseConfig.get_engine())
        
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False


if __name__ == "__main__":
    init_database()
