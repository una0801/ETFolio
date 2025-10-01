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
from app.core.logging import setup_logger
from app.models.etf import ETF
from app.schemas.etf import ETFCreate, ETFResponse, ETFAnalytics
from app.services.yfinance_service import YFinanceService
from app.services.analytics_service import AnalyticsService
from app.services.chart_service import ChartService
from app.data.korean_etfs import ALL_ETFS, KOREAN_ETFS, US_ETFS

# 로거 설정
logger = setup_logger(__name__)

router = APIRouter(prefix="/etf", tags=["ETF"])

# ThreadPoolExecutor for blocking I/O operations
executor = ThreadPoolExecutor(max_workers=10)


@router.get("/list")
async def get_etf_list(category: str = None, search: str = None):
    """
    사용 가능한 ETF 목록 조회
    
    Args:
        category: 카테고리 필터 (국내주식, 해외주식, 채권 등)
        search: 검색어 (이름 또는 티커)
    """
    logger.info(f"ETF 목록 조회: category={category}, search={search}")
    
    etfs = ALL_ETFS.copy()
    
    # 카테고리 필터
    if category:
        etfs = [etf for etf in etfs if etf["category"] == category]
    
    # 검색 필터
    if search:
        search_lower = search.lower()
        etfs = [
            etf for etf in etfs 
            if search_lower in etf["name"].lower() or search_lower in etf["ticker"].lower()
        ]
    
    logger.info(f"ETF 목록 반환: {len(etfs)}개")
    return {
        "total": len(etfs),
        "etfs": etfs
    }


@router.get("/categories")
async def get_categories():
    """ETF 카테고리 목록"""
    categories = list(set(etf["category"] for etf in ALL_ETFS))
    return {"categories": sorted(categories)}


@router.post("/", response_model=ETFResponse)
async def create_etf(etf: ETFCreate, db: Session = Depends(get_db)):
    """ETF 종목 추가 (비동기)"""
    logger.info(f"ETF 추가 요청: {etf.ticker}")
    try:
        # 티커 변환 (한국 ETF 이름 → yfinance 티커)
        ticker = YFinanceService.get_ticker(etf.ticker)
        logger.debug(f"티커 변환 완료: {etf.ticker} -> {ticker}")
        
        # 이미 존재하는지 확인
        existing_etf = db.query(ETF).filter(ETF.ticker == ticker).first()
        if existing_etf:
            logger.warning(f"이미 등록된 ETF: {ticker}")
            raise HTTPException(status_code=400, detail="이미 등록된 ETF입니다")
        
        # yfinance에서 ETF 정보 조회 (blocking I/O를 비동기로 처리)
        logger.info(f"yfinance에서 ETF 정보 조회 중: {ticker}")
        etf_info = await asyncio.to_thread(YFinanceService.get_etf_info, ticker)
        
        if not etf_info:
            logger.error(f"ETF 정보를 찾을 수 없음: {ticker}")
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
        
        logger.info(f"ETF 추가 성공: {ticker} - {db_etf.name}")
        return db_etf
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ETF 추가 중 오류 발생: {ticker} - {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"ETF 추가 중 오류: {str(e)}")


@router.get("/", response_model=List[ETFResponse])
async def get_etfs(db: Session = Depends(get_db)):
    """등록된 모든 ETF 조회 (비동기)"""
    etfs = await asyncio.to_thread(lambda: db.query(ETF).all())
    return etfs


@router.get("/{ticker}/info", response_model=ETFResponse)
async def get_etf_info(ticker: str, db: Session = Depends(get_db)):
    """특정 ETF 정보 조회 (비동기)"""
    etf = await asyncio.to_thread(
        lambda: db.query(ETF).filter(ETF.ticker == ticker).first()
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
    logger.info(f"ETF 분석 요청: {ticker}, 기간: {period}")
    try:
        # ETF 존재 확인
        etf = await asyncio.to_thread(
            lambda: db.query(ETF).filter(ETF.ticker == ticker).first()
        )
        if not etf:
            logger.warning(f"ETF를 찾을 수 없음: {ticker}")
            raise HTTPException(status_code=404, detail="ETF를 찾을 수 없습니다")
        
        logger.debug(f"ETF 정보 확인 완료: {etf.name}")
        
        # 병렬로 데이터 조회 (성능 최적화)
        logger.info(f"yfinance 데이터 조회 시작: {ticker}")
        hist, dividends = await asyncio.gather(
            asyncio.to_thread(YFinanceService.get_price_history, ticker, period),
            asyncio.to_thread(YFinanceService.get_dividends, ticker),
            return_exceptions=True
        )
        
        # 에러 체크
        if isinstance(hist, Exception):
            logger.error(f"가격 정보 조회 실패: {ticker} - {str(hist)}")
            raise HTTPException(status_code=500, detail=f"가격 정보 조회 실패: {str(hist)}")
        if isinstance(dividends, Exception):
            logger.warning(f"배당금 정보 조회 실패 (무시): {ticker} - {str(dividends)}")
            dividends = []
        
        if hist is None or hist.empty:
            logger.error(f"가격 정보가 비어있음: {ticker}")
            raise HTTPException(status_code=404, detail="가격 정보를 찾을 수 없습니다")
        
        if dividends is None:
            dividends = []
        
        logger.debug(f"데이터 조회 완료: 가격 데이터 {len(hist)}개, 배당금 {len(dividends) if hasattr(dividends, '__len__') else 0}개")
        
        # 현재 가격
        current_price = await asyncio.to_thread(YFinanceService.get_current_price, ticker)
        if not current_price:
            current_price = float(hist['Close'].iloc[-1])
            logger.debug(f"현재 가격을 마지막 종가로 사용: {current_price}")
        
        # 분석 수행
        logger.info(f"분석 수행 중: {ticker}")
        analytics = await asyncio.to_thread(
            AnalyticsService.analyze_etf, hist, dividends, current_price
        )
        
        logger.info(f"ETF 분석 완료: {ticker} - CAGR: {analytics.get('cagr', 0):.2f}%")
        
        return {
            "ticker": ticker,
            "name": etf.name,
            "current_price": float(current_price),
            **analytics
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ETF 분석 중 오류 발생: {ticker} - {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")


@router.get("/{ticker}/chart/price")
async def get_price_chart(ticker: str, period: str = "1y"):
    """가격 차트 조회 (비동기)"""
    logger.info(f"가격 차트 요청: {ticker}, 기간: {period}")
    try:
        hist = await asyncio.to_thread(YFinanceService.get_price_history, ticker, period)
        
        if hist is None or hist.empty:
            logger.warning(f"가격 정보 없음: {ticker}")
            raise HTTPException(status_code=404, detail="가격 정보를 찾을 수 없습니다")
        
        logger.debug(f"차트 생성 중: {ticker}, 데이터 {len(hist)}개")
        chart = await asyncio.to_thread(ChartService.create_price_chart, hist, ticker)
        logger.info(f"가격 차트 생성 완료: {ticker}")
        return {"chart": chart}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"차트 생성 중 오류: {ticker} - {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"차트 생성 중 오류: {str(e)}")


@router.get("/{ticker}/chart/dividend")
async def get_dividend_chart(ticker: str):
    """배당금 차트 조회 (비동기)"""
    try:
        dividends = await asyncio.to_thread(YFinanceService.get_dividends, ticker)
        
        if dividends is None:
            dividends = []
        
        chart = await asyncio.to_thread(ChartService.create_dividend_chart, dividends, ticker)
        return {"chart": chart}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"차트 생성 중 오류: {str(e)}")


@router.get("/{ticker}/chart/cumulative-return")
async def get_cumulative_return_chart(ticker: str, period: str = "1y"):
    """누적 수익률 차트 조회 (비동기)"""
    try:
        hist = await asyncio.to_thread(YFinanceService.get_price_history, ticker, period)
        
        if hist is None or hist.empty:
            raise HTTPException(status_code=404, detail="가격 정보를 찾을 수 없습니다")
        
        chart = await asyncio.to_thread(ChartService.create_cumulative_return_chart, hist, ticker)
        return {"chart": chart}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"차트 생성 중 오류: {str(e)}")


@router.delete("/{ticker}")
async def delete_etf(ticker: str, db: Session = Depends(get_db)):
    """ETF 삭제 (비동기)"""
    etf = await asyncio.to_thread(
        lambda: db.query(ETF).filter(ETF.ticker == ticker).first()
    )
    
    if not etf:
        raise HTTPException(status_code=404, detail="ETF를 찾을 수 없습니다")
    
    await asyncio.to_thread(lambda: (db.delete(etf), db.commit()))
    
    return {"message": "ETF가 삭제되었습니다"}

