from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv(override=True)

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./webhook.db")

is_sqlite = SQLALCHEMY_DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


try:
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN limit_destinations INT NULL"))
            conn.commit()
        except:
            pass
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN is_suspended BOOLEAN DEFAULT 0"))
            conn.commit()
        except:
            pass
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN reset_token VARCHAR(255) NULL"))
            conn.commit()
        except:
            pass
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN reset_token_expires DATETIME NULL"))
            conn.commit()
        except:
            pass
except:
    pass

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
