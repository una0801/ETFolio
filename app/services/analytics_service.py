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
        총 수익률 (Total Return) 계산
        
        공식: ((종가 - 시작가) / 시작가) × 100
        
        설명:
            - 단순히 처음 가격과 마지막 가격을 비교한 수익률
            - 복리 효과는 고려하지 않음 (단순 수익률)
            - 예: 100원 → 150원이면 50% 수익
        
        주의:
            - 기간이 다르면 비교가 어려움 (1년 50% vs 5년 50%는 다름)
            - 그래서 장기 투자는 CAGR을 사용하는 것이 더 정확함
        
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
        연평균 복리 수익률 (CAGR, Compound Annual Growth Rate) 계산
        
        공식: ((종가 / 시작가) ^ (1 / 년수) - 1) × 100
        
        설명:
            - "매년 평균적으로 몇 %씩 수익이 났는가?"를 계산
            - 복리 효과를 고려한 "진짜 연평균 수익률"
            - 기간이 달라도 비교 가능 (1년 투자든 10년 투자든)
        
        예시:
            100만원 → 5년 후 200만원
            - 총 수익률: 100%
            - CAGR: (200/100)^(1/5) - 1 = 14.87%
            - 의미: 매년 평균 14.87%씩 복리로 성장
        
        왜 CAGR을 쓰나?
            - 총 수익률은 기간이 다르면 비교 불가
            - CAGR은 "연평균"이므로 1년 투자 vs 10년 투자 비교 가능
            - 투자 업계 표준 지표
        
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
        years = (end_date - start_date).days / 365.25  # 윤년 고려
        
        if years <= 0:
            return 0.0
        
        # CAGR = (종가/시작가)^(1/년수) - 1
        cagr = (pow(end_price / start_price, 1 / years) - 1) * 100
        return cagr
    
    @staticmethod
    def calculate_volatility(hist: pd.DataFrame) -> float:
        """
        변동성 (Volatility) 계산 - 연환산 표준편차
        
        공식: 일일 수익률의 표준편차 × √252 × 100
        
        설명:
            - "가격이 얼마나 들쭉날쭉한가?"를 측정
            - 표준편차 = 평균에서 얼마나 벗어나는지
            - 변동성이 높다 = 가격이 요동친다 = 위험하다
            - 변동성이 낮다 = 가격이 안정적 = 안전하다
        
        계산 과정:
            1) 일일 수익률 계산: (오늘 가격 - 어제 가격) / 어제 가격
            2) 일일 수익률의 표준편차 계산
            3) √252를 곱해서 연환산 (1년 거래일 약 252일)
            4) 100을 곱해서 %로 변환
        
        왜 √252를 곱하나?
            - 변동성은 시간의 제곱근에 비례 (확률 이론)
            - 일일 변동성 → 연간 변동성 변환
            - 예: 일일 변동성 1% → 연간 15.87% (1% × √252)
        
        해석:
            - 10% 미만: 매우 안정적 (채권 ETF 수준)
            - 10~20%: 안정적 (대형주 ETF)
            - 20~30%: 보통 (일반 주식 ETF)
            - 30% 이상: 변동성 높음 (섹터 ETF, 레버리지 ETF)
        
        Returns:
            변동성 (%, 연환산)
        """
        if hist.empty or len(hist) < 2:
            return 0.0
        
        # 일일 수익률 계산
        daily_returns = hist['Close'].pct_change().dropna()
        
        # 연환산 변동성 = 일일 수익률 표준편차 × √252 × 100
        volatility = daily_returns.std() * np.sqrt(252) * 100
        return volatility
    
    @staticmethod
    def calculate_sharpe_ratio(hist: pd.DataFrame, risk_free_rate: float = 0.02) -> float:
        """
        샤프 비율 (Sharpe Ratio) 계산 - 위험 대비 수익의 효율성
        
        공식: (CAGR - 무위험 수익률) / 변동성
        
        설명:
            - "위험 1%당 얼마나 수익을 냈는가?"를 측정
            - 같은 수익률이라도 변동성이 낮으면 샤프 비율이 높음
            - 투자 효율성을 나타내는 가장 중요한 지표 중 하나
        
        계산 과정:
            1) 초과 수익률 = CAGR - 무위험 수익률 (예: 국채 수익률 2%)
               - 무위험 자산보다 얼마나 더 벌었는지
            2) 초과 수익률 ÷ 변동성
               - 감수한 위험 대비 얼마나 벌었는지
        
        예시:
            A ETF: CAGR 15%, 변동성 20%
              → 샤프 = (15 - 2) / 20 = 0.65
            
            B ETF: CAGR 15%, 변동성 10%
              → 샤프 = (15 - 2) / 10 = 1.30
              → 같은 수익이지만 B가 더 효율적!
        
        해석:
            - 1.0 미만: 효율성 낮음 (위험 대비 수익 부족)
            - 1.0 ~ 2.0: 양호 (일반적인 주식 ETF)
            - 2.0 ~ 3.0: 매우 좋음 (우수한 ETF)
            - 3.0 이상: 탁월함 (거의 없음, 의심해봐야 함)
        
        왜 무위험 수익률을 빼나?
            - 은행 예금이나 국채도 2% 정도는 벌 수 있음 (거의 무위험)
            - 주식 투자는 위험을 감수하는 것이므로
            - "무위험 수익률보다 얼마나 더 벌었는지"가 중요
        
        Args:
            hist: 가격 히스토리
            risk_free_rate: 무위험 수익률 (연율, 기본값 2% = 0.02)
        
        Returns:
            샤프 비율 (무단위)
        """
        if hist.empty or len(hist) < 2:
            return 0.0
        
        # 연환산 수익률
        cagr = AnalyticsService.calculate_cagr(hist)
        
        # 변동성
        volatility = AnalyticsService.calculate_volatility(hist)
        
        if volatility == 0:
            return 0.0
        
        # 샤프 비율 = (초과 수익률) / 변동성
        sharpe = (cagr - risk_free_rate * 100) / volatility
        return sharpe
    
    @staticmethod
    def calculate_max_drawdown(hist: pd.DataFrame) -> float:
        """
        최대 낙폭 (MDD, Maximum Drawdown) 계산
        
        공식: ((현재가 - 최고가) / 최고가) × 100 중 최솟값
        
        설명:
            - "역대 최고가에서 얼마나 떨어졌었는가?"를 측정
            - 투자 심리적으로 가장 중요한 지표
            - "내가 최악의 타이밍에 샀다면 얼마나 손해 봤을까?"
        
        계산 과정:
            1) 각 시점까지의 누적 최고가 계산
               - 예: [100, 110, 105, 120] → [100, 110, 110, 120]
            2) 현재가 - 누적 최고가 차이 계산
               - 예: 최고가 120에서 90까지 떨어졌다면 -30
            3) 비율로 환산: -30 / 120 = -25%
            4) 모든 기간 중 최악의 낙폭 선택
        
        예시:
            가격 변화: 100 → 150 → 120 → 180 → 100
            - 150에서 120: -20% 낙폭
            - 180에서 100: -44.4% 낙폭 ← MDD!
            
            MDD = 44.4%
            의미: 최악의 경우 44.4% 손실을 견뎌야 했음
        
        왜 중요한가?
            - 수익률이 높아도 MDD가 크면 심리적으로 버티기 어려움
            - 예: CAGR 20%, MDD 60% → 많은 사람이 손절하고 나감
            - 적립식 투자에서 특히 중요 (하락장에도 계속 사야 함)
        
        해석:
            - 10% 미만: 매우 안정적 (국채 수준)
            - 10~20%: 안정적 (배당 ETF, 대형주)
            - 20~30%: 보통 (일반 주식 ETF)
            - 30~50%: 높음 (섹터 ETF, 성장주)
            - 50% 이상: 매우 높음 (고위험 ETF, 레버리지)
        
        주의:
            - MDD는 "과거"의 최악 상황이며, 미래를 보장하지 않음
            - 하지만 과거에 큰 낙폭을 겪었다면 미래에도 비슷할 가능성 높음
        
        Returns:
            MDD (%, 절댓값)
        """
        if hist.empty or len(hist) < 2:
            return 0.0
        
        # 누적 최고가 계산 (각 시점까지의 역대 최고가)
        cummax = hist['Close'].cummax()
        
        # 낙폭 계산 (현재가 - 최고가) / 최고가
        drawdown = (hist['Close'] - cummax) / cummax * 100
        
        # 최대 낙폭 (가장 큰 마이너스 값)
        max_dd = drawdown.min()
        
        # 절댓값으로 반환 (음수 → 양수)
        return abs(max_dd)
    
    @staticmethod
    def calculate_dividend_yield(
        dividends,  # pd.Series 또는 list
        current_price: float
    ) -> float:
        """
        배당 수익률 (Dividend Yield) 계산
        
        공식: (연간 배당금 합계 / 현재 주가) × 100
        
        설명:
            - "주가 대비 연간 배당금이 얼마인가?"를 측정
            - 은행 이자율과 비교 가능한 지표
            - 시세 차익 외에 정기적인 현금 수입
        
        계산 과정:
            1) 최근 1년간 지급된 배당금 합계
            2) 현재 주가로 나누기
            3) 100을 곱해서 %로 변환
        
        예시:
            현재 주가: 10만원
            연간 배당금: 3,000원
            배당 수익률 = (3,000 / 100,000) × 100 = 3%
            
            의미: 주식을 보유하면 연간 3%의 현금 배당
        
        왜 중요한가?
            - 은퇴자나 현금 흐름이 필요한 사람에게 중요
            - 시장이 하락해도 배당금은 계속 나옴 (심리적 안정)
            - 배당을 재투자하면 복리 효과 (Dividend Reinvestment)
        
        배당 ETF 전략:
            - 고배당 ETF: SCHD, VYM, TIGER 미국배당귀족
            - 배당 수익률 3~5%: 양호
            - 배당 수익률 5% 이상: 매우 좋음 (단, 지속 가능성 확인 필요)
        
        주의사항:
            - 배당률이 너무 높으면 (>10%) 의심해볼 것
              → 회사가 어려워서 주가가 폭락했을 수도 있음
            - 배당 컷 (배당 삭감) 위험도 고려해야 함
            - 미국 ETF는 배당세 15% 원천징수됨 (한미 조세협약)
        
        Args:
            dividends: 배당금 히스토리 (날짜별 배당금)
            current_price: 현재 주가
        
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
        
        # 배당 수익률 = (연간 배당금 / 현재가) × 100
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

