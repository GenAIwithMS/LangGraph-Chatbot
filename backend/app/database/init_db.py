from app.database import DatabaseConfig
from app.database.models import Base


def init_database():
    try:
        Base.metadata.create_all(DatabaseConfig.get_engine())
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False


if __name__ == "__main__":
    init_database()
