# ETF 목록 실시간 수집 서비스
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import FinanceDataReader as fdr
import pandas as pd

from app.core.logging import setup_logger

logger = setup_logger(__name__)


class ETFListCache:
    """ETF 목록 캐시 관리 클래스"""
    
    def __init__(self, ttl_hours: int = 24):
        self._cache: Optional[List[Dict]] = None
        self._last_updated: Optional[datetime] = None
        self._ttl = timedelta(hours=ttl_hours)
        self._lock = asyncio.Lock()
    
    def is_expired(self) -> bool:
        """캐시 만료 여부 확인"""
        if self._last_updated is None:
            return True
        return datetime.now() - self._last_updated > self._ttl
    
    async def get(self) -> Optional[List[Dict]]:
        """캐시된 데이터 반환"""
        async with self._lock:
            if not self.is_expired():
                return self._cache
            return None
    
    async def set(self, data: List[Dict]):
        """캐시 데이터 저장"""
        async with self._lock:
            self._cache = data
            self._last_updated = datetime.now()
            logger.info(f"ETF 목록 캐시 업데이트 완료: {len(data)}개 종목")


class ETFListService:
    """실시간 ETF 목록 수집 서비스"""
    
    # 24시간 캐시
    _cache = ETFListCache(ttl_hours=24)
    
    @staticmethod
    async def _fetch_krx_etfs() -> List[Dict]:
        """한국거래소 ETF 목록 수집"""
        logger.info("KRX ETF 목록 수집 시작")
        try:
            # FinanceDataReader로 KRX ETF 목록 가져오기
            df = await asyncio.to_thread(fdr.StockListing, 'ETF/KR')
            
            etfs = []
            for _, row in df.iterrows():
                # Symbol 컬럼 사용 (Code가 아님)
                ticker = str(row['Symbol'])
                name = str(row['Name'])
                
                # yfinance 형식으로 변환 (.KS 또는 .KQ 추가)
                if not ticker.endswith('.KS') and not ticker.endswith('.KQ'):
                    ticker = f"{ticker}.KS"
                
                etfs.append({
                    "ticker": ticker,
                    "name": name,
                    "category": "한국 ETF",
                    "market": "KRX"
                })
            
            logger.info(f"KRX ETF 수집 완료: {len(etfs)}개")
            return etfs
        except Exception as e:
            logger.error(f"KRX ETF 수집 실패: {str(e)}", exc_info=True)
            return []
    
    @staticmethod
    async def _fetch_us_etfs() -> List[Dict]:
        """미국 주요 ETF 목록 수집"""
        logger.info("미국 ETF 목록 수집 시작")
        try:
            # NASDAQ ETF 목록 가져오기
            df = await asyncio.to_thread(fdr.StockListing, 'NASDAQ')
            
            # ETF만 필터링 (ETF는 보통 이름에 특정 패턴이 있음)
            etf_keywords = ['ETF', 'Trust', 'Fund', 'iShares', 'SPDR', 'Vanguard', 'Invesco']
            
            etfs = []
            for _, row in df.iterrows():
                name = str(row.get('Name', ''))
                # ETF 키워드가 포함된 종목만 선택
                if any(keyword.lower() in name.lower() for keyword in etf_keywords):
                    etfs.append({
                        "ticker": row['Symbol'],
                        "name": name,
                        "category": "미국 ETF",
                        "market": "NASDAQ"
                    })
            
            logger.info(f"미국 ETF 수집 완료: {len(etfs)}개")
            return etfs[:200]  # 너무 많으면 200개로 제한
        except Exception as e:
            logger.error(f"미국 ETF 수집 실패: {str(e)}", exc_info=True)
            return []
    
    @staticmethod
    async def _get_popular_us_etfs() -> List[Dict]:
        """주요 미국 ETF 하드코딩 목록 (백업용)"""
        return [
            {"ticker": "SPY", "name": "SPDR S&P 500 ETF Trust", "category": "미국 ETF - 대형주", "market": "US"},
            {"ticker": "QQQ", "name": "Invesco QQQ Trust", "category": "미국 ETF - 기술주", "market": "US"},
            {"ticker": "VOO", "name": "Vanguard S&P 500 ETF", "category": "미국 ETF - 대형주", "market": "US"},
            {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "category": "미국 ETF - 전체시장", "market": "US"},
            {"ticker": "IVV", "name": "iShares Core S&P 500 ETF", "category": "미국 ETF - 대형주", "market": "US"},
            {"ticker": "VEA", "name": "Vanguard FTSE Developed Markets ETF", "category": "미국 ETF - 선진국", "market": "US"},
            {"ticker": "IEFA", "name": "iShares Core MSCI EAFE ETF", "category": "미국 ETF - 선진국", "market": "US"},
            {"ticker": "AGG", "name": "iShares Core U.S. Aggregate Bond ETF", "category": "미국 ETF - 채권", "market": "US"},
            {"ticker": "VWO", "name": "Vanguard FTSE Emerging Markets ETF", "category": "미국 ETF - 신흥국", "market": "US"},
            {"ticker": "GLD", "name": "SPDR Gold Trust", "category": "미국 ETF - 금", "market": "US"},
            {"ticker": "BND", "name": "Vanguard Total Bond Market ETF", "category": "미국 ETF - 채권", "market": "US"},
            {"ticker": "VIG", "name": "Vanguard Dividend Appreciation ETF", "category": "미국 ETF - 배당", "market": "US"},
            {"ticker": "SCHD", "name": "Schwab U.S. Dividend Equity ETF", "category": "미국 ETF - 배당", "market": "US"},
            {"ticker": "VYM", "name": "Vanguard High Dividend Yield ETF", "category": "미국 ETF - 배당", "market": "US"},
            {"ticker": "VNQ", "name": "Vanguard Real Estate ETF", "category": "미국 ETF - 부동산", "market": "US"},
        ]
    
    @classmethod
    async def get_all_etfs(cls, force_refresh: bool = False) -> List[Dict]:
        """
        전체 ETF 목록 가져오기 (캐시 활용)
        
        Args:
            force_refresh: 캐시 무시하고 강제 새로고침
        
        Returns:
            ETF 목록 (ticker, name, category, market)
        """
        logger.info(f"ETF 목록 요청 (force_refresh={force_refresh})")
        
        # 캐시 확인
        if not force_refresh:
            cached = await cls._cache.get()
            if cached:
                logger.info(f"캐시된 ETF 목록 반환: {len(cached)}개")
                return cached
        
        # 실시간 수집
        logger.info("실시간 ETF 목록 수집 시작")
        try:
            # 한국 ETF와 미국 ETF 동시 수집
            krx_etfs, us_popular = await asyncio.gather(
                cls._fetch_krx_etfs(),
                cls._get_popular_us_etfs(),
                return_exceptions=True
            )
            
            # 예외 처리
            if isinstance(krx_etfs, Exception):
                logger.error(f"KRX ETF 수집 중 오류: {str(krx_etfs)}")
                krx_etfs = []
            
            if isinstance(us_popular, Exception):
                logger.error(f"미국 ETF 수집 중 오류: {str(us_popular)}")
                us_popular = []
            
            # 전체 목록 합치기
            all_etfs = krx_etfs + us_popular
            
            # 캐시 저장
            if all_etfs:
                await cls._cache.set(all_etfs)
            
            logger.info(f"전체 ETF 목록 수집 완료: {len(all_etfs)}개 (KRX: {len(krx_etfs)}, US: {len(us_popular)})")
            return all_etfs
            
        except Exception as e:
            logger.error(f"ETF 목록 수집 중 예상치 못한 오류: {str(e)}", exc_info=True)
            # 최소한 주요 미국 ETF라도 반환
            fallback = await cls._get_popular_us_etfs()
            return fallback
    
    @classmethod
    async def search_etfs(cls, query: str, limit: int = 50) -> List[Dict]:
        """
        ETF 검색
        
        Args:
            query: 검색어 (종목코드 또는 이름)
            limit: 최대 결과 개수
        
        Returns:
            검색된 ETF 목록
        """
        logger.info(f"ETF 검색: '{query}' (limit={limit})")
        
        all_etfs = await cls.get_all_etfs()
        
        if not query:
            return all_etfs[:limit]
        
        # 검색어로 필터링 (대소문자 구분 없음)
        query_lower = query.lower()
        filtered = [
            etf for etf in all_etfs
            if query_lower in etf['ticker'].lower() or query_lower in etf['name'].lower()
        ]
        
        logger.info(f"검색 결과: {len(filtered)}개 ('{query}')")
        return filtered[:limit]

