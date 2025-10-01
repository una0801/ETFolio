"""
데이터베이스 연결 및 세션 관리
비동기 처리를 위한 connection pooling 설정
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# SQLite 엔진 생성 (connection pooling 설정)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite용 설정
    poolclass=StaticPool,  # SQLite의 경우 StaticPool 사용
    pool_pre_ping=True,  # 연결 유효성 검사
    echo=settings.DEBUG,  # 디버그 모드에서 SQL 쿼리 로깅
)

# 세션 생성
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,  # 비동기 처리 시 유용
)

# Base 클래스 생성
Base = declarative_base()


def get_db():
    """
    데이터베이스 세션 의존성
    FastAPI dependency injection에서 사용
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """데이터베이스 초기화 (테이블 생성)"""
    Base.metadata.create_all(bind=engine)

