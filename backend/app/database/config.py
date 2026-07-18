import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


class DatabaseConfig:
    HOST = os.getenv("MYSQL_HOST", "localhost")
    PORT = int(os.getenv("MYSQL_PORT", "3306"))
    USER = os.getenv("MYSQL_USER", "root")
    PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    DATABASE = os.getenv("MYSQL_DATABASE", "chatbot_db")

    _engine = None
    _session_factory = None

    @classmethod
    def get_connection_url(cls) -> str:
        db_path = os.getenv("SQLITE_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "chatbot.db"))
        return f"sqlite:///{db_path}"

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            cls._engine = create_engine(
                cls.get_connection_url(),
                connect_args={"check_same_thread": False}
            )
        return cls._engine

    @classmethod
    def get_session_factory(cls):
        if cls._session_factory is None:
            cls._session_factory = sessionmaker(bind=cls.get_engine())
        return cls._session_factory

    @classmethod
    def create_session(cls):
        return cls.get_session_factory()()
