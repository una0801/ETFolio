"""
ETF 관련 데이터베이스 모델
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ETF(Base):
    """ETF 기본 정보 모델"""
    __tablename__ = "etfs"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)  # 종목 코드
    name = Column(String, nullable=False)  # ETF 이름
    market = Column(String)  # 시장 (KRX, NYSE 등)
    category = Column(String)  # 카테고리 (국내주식, 해외주식, 채권 등)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    holdings = relationship("Holding", back_populates="etf", cascade="all, delete-orphan")


class Holding(Base):
    """보유 ETF 정보 모델"""
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    etf_id = Column(Integer, ForeignKey("etfs.id"), nullable=False)
    quantity = Column(Float, nullable=False)  # 보유 수량
    average_price = Column(Float, nullable=False)  # 평균 매수가
    purchase_date = Column(DateTime, default=datetime.utcnow)  # 매수일
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    etf = relationship("ETF", back_populates="holdings")


class PriceHistory(Base):
    """가격 히스토리 모델 (캐싱용)"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)
    date = Column(DateTime, nullable=False)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    dividends = Column(Float, default=0)  # 배당금
    created_at = Column(DateTime, default=datetime.utcnow)

