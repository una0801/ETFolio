"""
ETF 관련 API 라우트
비동기 처리로 여러 사용자의 동시 요청 처리
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.database import get_db
from app.models.etf import ETF
from app.schemas.etf import ETFCreate, ETFResponse, ETFAnalytics
from app.services.yfinance_service import YFinanceService
from app.services.analytics_service import AnalyticsService
from app.services.chart_service import ChartService

router = APIRouter(prefix="/etf", tags=["ETF"])

# ThreadPoolExecutor for blocking I/O operations
executor = ThreadPoolExecutor(max_workers=10)


@router.post("/", response_model=ETFResponse)
async def create_etf(etf: ETFCreate, db: Session = Depends(get_db)):
    """ETF 종목 추가 (비동기)"""
    # 티커 변환 (한국 ETF 이름 → yfinance 티커)
    ticker = YFinanceService.get_ticker(etf.ticker)
    
    # 이미 존재하는지 확인
    existing_etf = db.query(ETF).filter(ETF.ticker == ticker).first()
    if existing_etf:
        raise HTTPException(status_code=400, detail="이미 등록된 ETF입니다")
    
    # yfinance에서 ETF 정보 조회 (blocking I/O를 비동기로 처리)
    loop = asyncio.get_event_loop()
    etf_info = await loop.run_in_executor(
        executor, YFinanceService.get_etf_info, ticker
    )
    
    if not etf_info:
        raise HTTPException(status_code=404, detail="ETF 정보를 찾을 수 없습니다")
    
    # DB에 저장
    db_etf = ETF(
        ticker=ticker,
        name=etf_info.get("name", etf.name),
        market=etf.market or etf_info.get("exchange"),
        category=etf.category or etf_info.get("category")
    )
    db.add(db_etf)
    db.commit()
    db.refresh(db_etf)
    
    return db_etf


@router.get("/", response_model=List[ETFResponse])
async def get_etfs(db: Session = Depends(get_db)):
    """등록된 모든 ETF 조회 (비동기)"""
    loop = asyncio.get_event_loop()
    etfs = await loop.run_in_executor(
        executor, lambda: db.query(ETF).all()
    )
    return etfs


@router.get("/{ticker}/info", response_model=ETFResponse)
async def get_etf_info(ticker: str, db: Session = Depends(get_db)):
    """특정 ETF 정보 조회 (비동기)"""
    loop = asyncio.get_event_loop()
    etf = await loop.run_in_executor(
        executor, lambda: db.query(ETF).filter(ETF.ticker == ticker).first()
    )
    if not etf:
        raise HTTPException(status_code=404, detail="ETF를 찾을 수 없습니다")
    return etf


@router.get("/{ticker}/analytics")
async def get_etf_analytics(
    ticker: str, 
    period: str = "1y",
    db: Session = Depends(get_db)
):
    """ETF 분석 정보 조회 (비동기)"""
    loop = asyncio.get_event_loop()
    
    # ETF 존재 확인
    etf = await loop.run_in_executor(
        executor, lambda: db.query(ETF).filter(ETF.ticker == ticker).first()
    )
    if not etf:
        raise HTTPException(status_code=404, detail="ETF를 찾을 수 없습니다")
    
    # 병렬로 데이터 조회 (성능 최적화)
    hist_task = loop.run_in_executor(
        executor, YFinanceService.get_price_history, ticker, period
    )
    div_task = loop.run_in_executor(
        executor, YFinanceService.get_dividends, ticker
    )
    
    hist, dividends = await asyncio.gather(hist_task, div_task)
    
    if hist is None or hist.empty:
        raise HTTPException(status_code=404, detail="가격 정보를 찾을 수 없습니다")
    
    if dividends is None:
        dividends = []
    
    # 현재 가격
    current_price = await loop.run_in_executor(
        executor, YFinanceService.get_current_price, ticker
    )
    if not current_price:
        current_price = hist['Close'].iloc[-1]
    
    # 분석 수행
    analytics = await loop.run_in_executor(
        executor, AnalyticsService.analyze_etf, hist, dividends, current_price
    )
    
    return {
        "ticker": ticker,
        "name": etf.name,
        "current_price": current_price,
        **analytics
    }


@router.get("/{ticker}/chart/price")
async def get_price_chart(ticker: str, period: str = "1y"):
    """가격 차트 조회 (비동기)"""
    loop = asyncio.get_event_loop()
    hist = await loop.run_in_executor(
        executor, YFinanceService.get_price_history, ticker, period
    )
    
    if hist is None or hist.empty:
        raise HTTPException(status_code=404, detail="가격 정보를 찾을 수 없습니다")
    
    chart = await loop.run_in_executor(
        executor, ChartService.create_price_chart, hist, ticker
    )
    return {"chart": chart}


@router.get("/{ticker}/chart/dividend")
async def get_dividend_chart(ticker: str):
    """배당금 차트 조회 (비동기)"""
    loop = asyncio.get_event_loop()
    dividends = await loop.run_in_executor(
        executor, YFinanceService.get_dividends, ticker
    )
    
    if dividends is None:
        dividends = []
    
    chart = await loop.run_in_executor(
        executor, ChartService.create_dividend_chart, dividends, ticker
    )
    return {"chart": chart}


@router.get("/{ticker}/chart/cumulative-return")
async def get_cumulative_return_chart(ticker: str, period: str = "1y"):
    """누적 수익률 차트 조회 (비동기)"""
    loop = asyncio.get_event_loop()
    hist = await loop.run_in_executor(
        executor, YFinanceService.get_price_history, ticker, period
    )
    
    if hist is None or hist.empty:
        raise HTTPException(status_code=404, detail="가격 정보를 찾을 수 없습니다")
    
    chart = await loop.run_in_executor(
        executor, ChartService.create_cumulative_return_chart, hist, ticker
    )
    return {"chart": chart}


@router.delete("/{ticker}")
async def delete_etf(ticker: str, db: Session = Depends(get_db)):
    """ETF 삭제 (비동기)"""
    loop = asyncio.get_event_loop()
    etf = await loop.run_in_executor(
        executor, lambda: db.query(ETF).filter(ETF.ticker == ticker).first()
    )
    
    if not etf:
        raise HTTPException(status_code=404, detail="ETF를 찾을 수 없습니다")
    
    await loop.run_in_executor(
        executor, lambda: (db.delete(etf), db.commit())
    )
    
    return {"message": "ETF가 삭제되었습니다"}

