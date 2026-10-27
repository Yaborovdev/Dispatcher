from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker


class Database:
    def __init__(self, config: dict):
        self.config = config
        self.engine = None
        self.SessionLocal = None

    def connect(self) -> None:
        url = URL.create(
            drivername="postgresql+psycopg",
            username=self.config["user"],
            password=self.config["password"],
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["name"],
        )
        self.engine = create_engine(url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)

    def test_connection(self) -> tuple[bool, str]:
        """Проверка подключения без создания таблиц."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True, "Подключение успешно"
        except Exception as e:
            return False, str(e)

    def get_session(self):
        return self.SessionLocal()

    @contextmanager
    def session_scope(self):
        """Сессия с автоматическим commit / rollback / close."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()