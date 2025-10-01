"""
yfinance를 활용한 ETF 데이터 조회 서비스
"""
import yfinance as yf
import pandas as pd
from typing import Optional, Dict
from datetime import datetime, timedelta


class YFinanceService:
    """yfinance 데이터 조회 서비스 클래스"""
    
    # 한국 ETF 티커 매핑 (예시)
    KOREAN_ETF_MAP = {
        "KODEX 200": "069500.KS",
        "KODEX S&P500": "360750.KS",
        "TIGER 미국배당귀족": "458730.KS",
        "TIGER 미국나스닥100": "133690.KS",
        "KODEX 미국나스닥100TR": "379800.KS",
    }
    
    @staticmethod
    def get_ticker(symbol: str) -> str:
        """
        티커 심볼 변환
        한국 ETF 이름을 입력받으면 yfinance 티커로 변환
        """
        return YFinanceService.KOREAN_ETF_MAP.get(symbol, symbol)
    
    @staticmethod
    def get_etf_info(ticker: str) -> Optional[Dict]:
        """ETF 기본 정보 조회"""
        try:
            etf = yf.Ticker(ticker)
            info = etf.info
            
            return {
                "ticker": ticker,
                "name": info.get("longName", info.get("shortName", ticker)),
                "category": info.get("category", ""),
                "currency": info.get("currency", ""),
                "exchange": info.get("exchange", ""),
            }
        except Exception as e:
            print(f"ETF 정보 조회 실패: {e}")
            return None
    
    @staticmethod
    def get_price_history(
        ticker: str, 
        period: str = "1y",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> Optional[pd.DataFrame]:
        """
        가격 히스토리 조회
        
        Args:
            ticker: 종목 코드
            period: 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            start: 시작일
            end: 종료일
        """
        try:
            etf = yf.Ticker(ticker)
            
            if start and end:
                hist = etf.history(start=start, end=end)
            else:
                hist = etf.history(period=period)
            
            return hist
        except Exception as e:
            print(f"가격 히스토리 조회 실패: {e}")
            return None
    
    @staticmethod
    def get_dividends(ticker: str, years: int = 5) -> Optional[pd.Series]:
        """배당금 히스토리 조회"""
        try:
            etf = yf.Ticker(ticker)
            dividends = etf.dividends
            
            # 최근 N년 데이터만 필터링
            cutoff_date = datetime.now() - timedelta(days=years * 365)
            dividends = dividends[dividends.index >= cutoff_date]
            
            return dividends
        except Exception as e:
            print(f"배당금 조회 실패: {e}")
            return None
    
    @staticmethod
    def get_current_price(ticker: str) -> Optional[float]:
        """현재 가격 조회"""
        try:
            etf = yf.Ticker(ticker)
            hist = etf.history(period="1d")
            
            if not hist.empty:
                return hist['Close'].iloc[-1]
            return None
        except Exception as e:
            print(f"현재 가격 조회 실패: {e}")
            return None

