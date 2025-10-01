"""
ETF 관련 Pydantic 스키마
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ETFBase(BaseModel):
    """ETF 기본 스키마"""
    ticker: str = Field(..., description="종목 코드")
    name: str = Field(..., description="ETF 이름")
    market: Optional[str] = Field(None, description="시장")
    category: Optional[str] = Field(None, description="카테고리")


class ETFCreate(ETFBase):
    """ETF 생성 스키마"""
    pass


class ETFResponse(ETFBase):
    """ETF 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HoldingBase(BaseModel):
    """보유 ETF 기본 스키마"""
    etf_id: int = Field(..., description="ETF ID")
    quantity: float = Field(..., gt=0, description="보유 수량")
    average_price: float = Field(..., gt=0, description="평균 매수가")
    purchase_date: Optional[datetime] = Field(None, description="매수일")


class HoldingCreate(HoldingBase):
    """보유 ETF 생성 스키마"""
    pass


class HoldingResponse(HoldingBase):
    """보유 ETF 응답 스키마"""
    id: int
    etf: ETFResponse
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ETFAnalytics(BaseModel):
    """ETF 분석 정보 스키마"""
    ticker: str
    name: str
    current_price: float
    total_return: float  # 총 수익률 (%)
    cagr: float  # 연평균 복리 수익률 (%)
    volatility: float  # 변동성 (%)
    sharpe_ratio: float  # 샤프 비율
    max_drawdown: float  # 최대 낙폭 (%)
    dividend_yield: float  # 배당 수익률 (%)
    total_dividends: float  # 총 배당금


class PortfolioSummary(BaseModel):
    """포트폴리오 요약 스키마"""
    total_investment: float  # 총 투자금액
    current_value: float  # 현재 평가액
    total_return: float  # 총 수익
    return_rate: float  # 수익률 (%)
    total_dividends: float  # 총 배당금
    holdings: List[HoldingResponse]

