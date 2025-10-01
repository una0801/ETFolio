"""
ETF 분석 서비스 (수익률, CAGR, 샤프 비율 등 계산)
"""
import numpy as np
import pandas as pd
from typing import Dict
from datetime import datetime

from app.core.logging import setup_logger

logger = setup_logger(__name__)


class AnalyticsService:
    """투자 분석 서비스 클래스"""
    
    @staticmethod
    def calculate_total_return(hist: pd.DataFrame) -> float:
        """
        총 수익률 계산
        
        Returns:
            수익률 (%)
        """
        if hist.empty or len(hist) < 2:
            return 0.0
        
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        
        return ((end_price - start_price) / start_price) * 100
    
    @staticmethod
    def calculate_cagr(hist: pd.DataFrame) -> float:
        """
        연평균 복리 수익률 (CAGR) 계산
        
        Returns:
            CAGR (%)
        """
        if hist.empty or len(hist) < 2:
            return 0.0
        
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        
        # 기간 계산 (년 단위)
        start_date = hist.index[0]
        end_date = hist.index[-1]
        years = (end_date - start_date).days / 365.25
        
        if years <= 0:
            return 0.0
        
        cagr = (pow(end_price / start_price, 1 / years) - 1) * 100
        return cagr
    
    @staticmethod
    def calculate_volatility(hist: pd.DataFrame) -> float:
        """
        변동성 계산 (연환산 표준편차)
        
        Returns:
            변동성 (%)
        """
        if hist.empty or len(hist) < 2:
            return 0.0
        
        # 일일 수익률 계산
        daily_returns = hist['Close'].pct_change().dropna()
        
        # 연환산 변동성
        volatility = daily_returns.std() * np.sqrt(252) * 100
        return volatility
    
    @staticmethod
    def calculate_sharpe_ratio(hist: pd.DataFrame, risk_free_rate: float = 0.02) -> float:
        """
        샤프 비율 계산 (위험 대비 수익률)
        
        Args:
            hist: 가격 히스토리
            risk_free_rate: 무위험 수익률 (연율, 기본값 2%)
        
        Returns:
            샤프 비율
        """
        if hist.empty or len(hist) < 2:
            return 0.0
        
        # 연환산 수익률
        cagr = AnalyticsService.calculate_cagr(hist)
        
        # 변동성
        volatility = AnalyticsService.calculate_volatility(hist)
        
        if volatility == 0:
            return 0.0
        
        sharpe = (cagr - risk_free_rate * 100) / volatility
        return sharpe
    
    @staticmethod
    def calculate_max_drawdown(hist: pd.DataFrame) -> float:
        """
        최대 낙폭 (MDD) 계산
        
        Returns:
            MDD (%)
        """
        if hist.empty or len(hist) < 2:
            return 0.0
        
        # 누적 최고가 계산
        cummax = hist['Close'].cummax()
        
        # 낙폭 계산
        drawdown = (hist['Close'] - cummax) / cummax * 100
        
        # 최대 낙폭
        max_dd = drawdown.min()
        return abs(max_dd)
    
    @staticmethod
    def calculate_dividend_yield(
        dividends,  # pd.Series 또는 list
        current_price: float
    ) -> float:
        """
        배당 수익률 계산
        
        Args:
            dividends: 배당금 히스토리
            current_price: 현재 가격
        
        Returns:
            배당 수익률 (%)
        """
        # dividends가 list이거나 None인 경우 빈 Series로 변환
        if isinstance(dividends, list) or dividends is None:
            dividends = pd.Series(dtype=float)
        
        if dividends.empty or current_price == 0:
            return 0.0
        
        # 최근 1년 배당금 합계
        one_year_ago = datetime.now() - pd.DateOffset(years=1)
        recent_dividends = dividends[dividends.index >= one_year_ago]
        
        total_div = recent_dividends.sum()
        div_yield = (total_div / current_price) * 100
        
        return float(div_yield)
    
    @staticmethod
    def analyze_etf(
        hist: pd.DataFrame,
        dividends,  # pd.Series 또는 list
        current_price: float
    ) -> Dict:
        """
        종합 분석 결과 반환
        """
        logger.info("ETF 종합 분석 시작")
        try:
            # dividends가 list인 경우 빈 Series로 변환
            if isinstance(dividends, list) or dividends is None:
                dividends = pd.Series(dtype=float)
            
            logger.debug(f"분석 데이터: 가격 {len(hist)}개, 배당 {len(dividends)}개, 현재가 {current_price}")
            
            result = {
                "total_return": AnalyticsService.calculate_total_return(hist),
                "cagr": AnalyticsService.calculate_cagr(hist),
                "volatility": AnalyticsService.calculate_volatility(hist),
                "sharpe_ratio": AnalyticsService.calculate_sharpe_ratio(hist),
                "max_drawdown": AnalyticsService.calculate_max_drawdown(hist),
                "dividend_yield": AnalyticsService.calculate_dividend_yield(dividends, current_price),
                "total_dividends": float(dividends.sum()) if not dividends.empty else 0.0,
            }
            
            logger.info(f"분석 완료: CAGR={result['cagr']:.2f}%, 변동성={result['volatility']:.2f}%")
            return result
            
        except Exception as e:
            logger.error(f"ETF 분석 중 오류: {str(e)}", exc_info=True)
            raise

