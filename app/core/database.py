"""
데이터베이스 연결 및 세션 관리
비동기 처리를 위한 connection pooling 설정
PostgreSQL(Vercel) 또는 SQLite(로컬) 자동 전환
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool, QueuePool

from app.core.config import settings

# 데이터베이스 URL 확인
db_url = settings.db_url
is_postgres = db_url.startswith("postgres")

# PostgreSQL vs SQLite에 따라 설정 분기
if is_postgres:
    # PostgreSQL 설정 (프로덕션)
    engine = create_engine(
        db_url,
        pool_size=20,           # 동시 연결 수
        max_overflow=10,        # 풀 초과 시 추가 연결
        pool_pre_ping=True,     # 연결 유효성 검사
        pool_recycle=3600,      # 1시간마다 연결 재생성
        echo=settings.DEBUG,
    )
else:
    # SQLite 설정 (로컬 개발)
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        pool_pre_ping=True,
        echo=settings.DEBUG,
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

