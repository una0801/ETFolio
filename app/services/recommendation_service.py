# ETF 추천 서비스
import asyncio
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime

from app.services.etf_list_service import ETFListService
from app.services.yfinance_service import YFinanceService
from app.services.analytics_service import AnalyticsService
from app.core.logging import setup_logger

logger = setup_logger(__name__)


class RecommendationService:
    """ETF 추천 서비스"""
    
    # 주요 ETF 목록 (분석 대상)
    FEATURED_KOREAN_ETFS = [
        "069500.KS",  # KODEX 200
        "360750.KS",  # TIGER 미국S&P500
        "133690.KS",  # TIGER 미국나스닥100
        "379800.KS",  # KODEX 미국S&P500
        "381170.KS",  # TIGER 미국테크TOP10
        "458750.KS",  # TIGER 미국배당다우존스
        "143850.KS",  # TIGER 미국S&P500선물(H)
        "102110.KS",  # TIGER 200
        "278530.KS",  # KODEX 200TR
        "091180.KS",  # KODEX 배당성장
    ]
    
    FEATURED_US_ETFS = [
        "SPY",   # SPDR S&P 500
        "QQQ",   # Invesco QQQ (나스닥100)
        "VOO",   # Vanguard S&P 500
        "VTI",   # Vanguard Total Stock Market
        "VIG",   # Vanguard Dividend Appreciation
        "SCHD",  # Schwab US Dividend Equity
        "VYM",   # Vanguard High Dividend Yield
        "IVV",   # iShares Core S&P 500
        "VEA",   # Vanguard FTSE Developed Markets
        "AGG",   # iShares Core US Aggregate Bond
    ]
    
    @staticmethod
    async def _analyze_etf(ticker: str, period: str = "5y") -> Optional[Dict]:
        """
        개별 ETF 분석
        
        Returns:
            분석 결과 또는 None (실패 시)
        """
        try:
            # 가격 및 배당 데이터 수집
            hist, dividends, info = await asyncio.gather(
                asyncio.to_thread(YFinanceService.get_price_history, ticker, period),
                asyncio.to_thread(YFinanceService.get_dividends, ticker),
                asyncio.to_thread(YFinanceService.get_etf_info, ticker),
                return_exceptions=True
            )
            
            # 에러 처리
            if isinstance(hist, Exception) or hist is None or hist.empty:
                logger.warning(f"{ticker} 가격 데이터 없음")
                return None
            
            if isinstance(dividends, Exception):
                dividends = pd.Series(dtype=float)
            
            if isinstance(info, Exception) or info is None:
                info = {"name": ticker}
            
            # 현재가
            current_price = float(hist['Close'].iloc[-1])
            
            # 분석 수행
            analytics = AnalyticsService.analyze_etf(hist, dividends, current_price)
            
            # 거래량 및 자산 정보 (yfinance info에서 추출)
            avg_volume = hist.get('Volume', pd.Series([0])).mean() if 'Volume' in hist.columns else 0
            total_assets = info.get("totalAssets", 0) if info else 0
            
            return {
                "ticker": ticker,
                "name": info.get("name", ticker),
                "current_price": current_price,
                "cagr": analytics.get("cagr", 0),
                "volatility": analytics.get("volatility", 0),
                "sharpe_ratio": analytics.get("sharpe_ratio", 0),
                "max_drawdown": analytics.get("max_drawdown", 0),
                "dividend_yield": analytics.get("dividend_yield", 0),
                "total_return": analytics.get("total_return", 0),
                "data_points": len(hist),
                "avg_volume": float(avg_volume),
                "total_assets": float(total_assets) if total_assets else 0
            }
            
        except Exception as e:
            logger.error(f"{ticker} 분석 실패: {str(e)}")
            return None
    
    @classmethod
    async def get_recommended_etfs(
        cls,
        category_filter: str = "korean",
        period: str = "5y",
        limit: int = 5
    ) -> Dict:
        """
        최고 성과 ETF 추천
        
        Args:
            category_filter: 'korean', 'us', 'all'
            period: 분석 기간
            limit: 추천 개수
        
        Returns:
            카테고리별 추천 ETF
        """
        category = category_filter
        logger.info(f"ETF 추천 시작: category={category}, period={period}, limit={limit}")
        
        # 분석 대상 선정
        if category == "korean":
            tickers = cls.FEATURED_KOREAN_ETFS
        elif category == "us":
            tickers = cls.FEATURED_US_ETFS
        else:
            tickers = cls.FEATURED_KOREAN_ETFS + cls.FEATURED_US_ETFS
        
        # 병렬로 모든 ETF 분석
        results = await asyncio.gather(
            *[cls._analyze_etf(ticker, period) for ticker in tickers],
            return_exceptions=True
        )
        
        # 성공한 결과만 필터링
        valid_results = [r for r in results if r is not None and not isinstance(r, Exception)]
        
        if not valid_results:
            logger.warning("분석 가능한 ETF 없음")
            return {
                "high_return": [],
                "stable": [],
                "high_dividend": [],
                "balanced": [],
                "metadata": {
                    "total_analyzed": 0,
                    "period": period,
                    "category": category
                }
            }
        
        logger.info(f"{len(valid_results)}/{len(tickers)}개 ETF 분석 완료")
        
        # 데이터 포인트가 충분한 것만 (최소 100일)
        valid_results = [r for r in valid_results if r["data_points"] >= 100]
        
        # ==================== 카테고리별 추천 로직 ====================
        # 각 카테고리는 서로 다른 투자 성향과 목표를 가진 투자자를 위해 설계되었습니다.
        
        recommendations = {
            # ---------- 1. 고수익형 (High Return) ----------
            # 목적: 단순히 높은 수익률을 추구하는 공격적 투자자용
            # 기준: CAGR (연평균 복리 수익률)만 고려
            # 특징: 변동성이나 위험은 고려하지 않음. 수익률이 최우선
            # 적합 대상: 높은 위험을 감수할 수 있고, 장기 투자 가능한 투자자
            "high_return": sorted(
                valid_results,
                key=lambda x: x["cagr"],
                reverse=True
            )[:limit],
            
            # ---------- 2. 안정형 (Stable) ----------
            # 목적: 안정적이면서도 효율적인 수익을 원하는 보수적 투자자용
            # 기준: 샤프 비율 ÷ (변동성 + 1)
            #   - 샤프 비율: 위험 대비 수익의 효율성 (높을수록 좋음)
            #   - 변동성으로 나누는 이유: 같은 샤프 비율이라도 변동성이 낮은 것을 우선
            #   - +1을 하는 이유: 0으로 나누는 것을 방지하고, 극단적인 값 완화
            # 특징: 수익률보다는 "안정적인 수익"을 중시
            # 적합 대상: 은퇴 준비, 원금 보존 중시, 변동성을 싫어하는 투자자
            "stable": sorted(
                valid_results,
                key=lambda x: x["sharpe_ratio"] / (x["volatility"] + 1),
                reverse=True
            )[:limit],
            
            # ---------- 3. 고배당형 (High Dividend) ----------
            # 목적: 정기적인 현금 흐름(배당금)을 원하는 투자자용
            # 기준: 연간 배당 수익률 (Dividend Yield)
            # 특징: 시세 차익보다 배당 소득에 집중
            # 적합 대상: 은퇴자, 현금 흐름이 필요한 사람, 배당 재투자 전략
            # 참고: 배당이 없는 ETF는 제외됨
            "high_dividend": sorted(
                [r for r in valid_results if r["dividend_yield"] > 0],
                key=lambda x: x["dividend_yield"],
                reverse=True
            )[:limit],
            
            # ---------- 4. 균형형 (Balanced) ----------
            # 목적: 수익성, 안정성, 위험 관리를 종합적으로 고려한 투자자용
            # 점수 계산: CAGR × 40% + 샤프비율 × 20 + (100 - MDD) × 40%
            #   1) CAGR × 0.4: 수익률 40% 반영
            #   2) 샤프 비율 × 20: 위험 대비 효율성 20% 반영 (×20은 스케일 조정)
            #   3) (100 - MDD) × 0.4: 최대 낙폭의 역수 40% 반영
            #      - MDD가 -30%라면 → (100 - 30) = 70점
            #      - 낙폭이 적을수록 높은 점수
            # 가중치 이유:
            #   - MDD 40%: 손실 방어가 장기 투자에서 매우 중요
            #   - CAGR 40%: 수익률도 중요하지만 MDD와 동등하게
            #   - 샤프 20%: 효율성은 보조 지표로 활용
            # 특징: 가장 밸런스 잡힌 추천
            # 적합 대상: 대부분의 일반 투자자
            "balanced": sorted(
                valid_results,
                key=lambda x: (
                    x["cagr"] * 0.4 +
                    x["sharpe_ratio"] * 20 +
                    (100 - abs(x["max_drawdown"])) * 0.4
                ),
                reverse=True
            )[:limit],
            
            # ---------- 5. 적립식 투자 (Monthly Investing / Dollar-Cost Averaging) ----------
            # 목적: 매달 일정 금액을 투자하는 "적립식 투자"에 최적화된 ETF
            # 점수 계산: (100 - MDD) × 50% + CAGR × 30% + (20 - 변동성) × 20%
            #   1) (100 - MDD) × 0.5: 최대 낙폭 최소화 50% 반영
            #      - 적립식은 하락장에서도 계속 사야 하므로 큰 낙폭은 심리적 부담
            #      - 낙폭이 적으면 "안심하고 꾸준히 투자" 가능
            #   2) CAGR × 0.3: 수익률 30% 반영
            #      - 너무 낮은 수익률은 의미 없으므로 적절한 수익률 필요
            #   3) (20 - 변동성) × 0.2: 낮은 변동성 20% 반영
            #      - 변동성 20% 이상이면 0점 처리
            #      - 변동성이 낮아야 매달 일정 금액 투자 시 평균 단가 안정
            # 가중치 이유:
            #   - MDD 50%: 적립식 투자자는 "하락에 대한 두려움"이 가장 큼
            #   - CAGR 30%: 장기적으로 우상향하는 ETF여야 함
            #   - 변동성 20%: 보조 지표, 너무 들쭉날쭉하면 심리적 부담
            # 특징: 초보자, 직장인이 매달 월급으로 투자하기 좋음
            # 적합 대상: 월급쟁이, 장기 적립식 투자자, 초보 투자자
            "monthly_investing": sorted(
                valid_results,
                key=lambda x: (
                    (100 - abs(x["max_drawdown"])) * 0.5 +
                    x["cagr"] * 0.3 +
                    (20 - min(x["volatility"], 20)) * 0.2
                ),
                reverse=True
            )[:limit],
            
            # ---------- 6. 인기순 (Popular / High Volume) ----------
            # 목적: 시장에서 가장 활발히 거래되는 ETF
            # 기준: 평균 일일 거래량
            # 이유:
            #   - 거래량이 많다 = 유동성이 좋다 = 사고팔기 쉽다
            #   - 스프레드(매수/매도 호가 차이)가 좁아 거래 비용 절감
            #   - 많은 사람들이 거래한다 = 시장에서 검증된 ETF
            # 특징: 실시간 매매가 잦은 투자자에게 유리
            # 적합 대상: 단기 매매자, 유동성 중시 투자자
            # 주의: 거래량 많다고 수익률이 좋은 건 아님
            "popular": sorted(
                valid_results,
                key=lambda x: x["avg_volume"],
                reverse=True
            )[:limit],
            
            # ---------- 7. 투자유치 TOP (High AUM / Assets Under Management) ----------
            # 목적: 가장 많은 자산이 투자된 대형 ETF
            # 기준: 총 자산 규모 (AUM)
            # 이유:
            #   - 자산이 크다 = 기관 투자자들이 신뢰한다
            #   - 대형 ETF는 상장폐지 위험이 거의 없음
            #   - 운용 규모의 경제로 보수(수수료)가 낮은 경우가 많음
            #   - 유동성이 뛰어나고 안정적
            # 특징: 가장 "검증된" ETF들
            # 적합 대상: 안정성과 신뢰성을 최우선시하는 투자자
            # 예시: SPY(SPDR S&P 500)는 세계에서 가장 큰 ETF 중 하나
            "high_aum": sorted(
                [r for r in valid_results if r["total_assets"] > 0],
                key=lambda x: x["total_assets"],
                reverse=True
            )[:limit],
            
            "metadata": {
                "total_analyzed": len(valid_results),
                "total_requested": len(tickers),
                "period": period,
                "category": category,
                "analyzed_at": datetime.now().isoformat()
            }
        }
        
        logger.info(f"ETF 추천 완료: {len(valid_results)}개 분석")
        return recommendations
    
    @staticmethod
    def _calculate_score(etf: Dict) -> float:
        """
        ETF 종합 점수 계산 (0~100점)
        
        - CAGR: 40%
        - 샤프 비율: 30%
        - MDD (역수): 20%
        - 배당 수익률: 10%
        """
        cagr_score = min(max(etf["cagr"], 0), 30) / 30 * 40  # 0~30% CAGR를 0~40점으로
        sharpe_score = min(max(etf["sharpe_ratio"], 0), 3) / 3 * 30  # 0~3 샤프를 0~30점으로
        mdd_score = (100 - min(abs(etf["max_drawdown"]), 50)) / 50 * 20  # MDD 역수
        dividend_score = min(etf["dividend_yield"], 5) / 5 * 10  # 0~5% 배당을 0~10점으로
        
        return cagr_score + sharpe_score + mdd_score + dividend_score

