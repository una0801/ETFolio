# 포트폴리오 상관관계 분석 서비스
import asyncio
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.services.yfinance_service import YFinanceService
from app.core.logging import setup_logger

logger = setup_logger(__name__)


class CorrelationService:
    """포트폴리오 상관관계 분석 서비스"""
    
    @staticmethod
    async def calculate_correlation_matrix(
        tickers: List[str],
        period: str = "1y"
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        여러 ETF의 가격 상관관계 매트릭스 계산
        
        Args:
            tickers: ETF 티커 리스트
            period: 분석 기간 (1mo, 3mo, 6mo, 1y, 2y, 5y)
        
        Returns:
            (상관관계 매트릭스, 메타데이터)
        """
        logger.info(f"상관관계 분석 시작: {len(tickers)}개 종목, 기간: {period}")
        
        if len(tickers) < 2:
            raise ValueError("최소 2개 이상의 ETF가 필요합니다")
        
        # 모든 ETF의 가격 데이터 동시 수집
        price_data_list = await asyncio.gather(
            *[asyncio.to_thread(YFinanceService.get_price_history, ticker, period) 
              for ticker in tickers],
            return_exceptions=True
        )
        
        # 데이터 수집 성공 여부 확인
        valid_data = {}
        failed_tickers = []
        
        for ticker, data in zip(tickers, price_data_list):
            if isinstance(data, Exception):
                logger.warning(f"{ticker} 데이터 수집 실패: {str(data)}")
                failed_tickers.append(ticker)
            elif data is None or data.empty:
                logger.warning(f"{ticker} 데이터 없음")
                failed_tickers.append(ticker)
            else:
                valid_data[ticker] = data['Close']
        
        if len(valid_data) < 2:
            raise ValueError(f"충분한 데이터를 가져올 수 없습니다. 실패: {failed_tickers}")
        
        # DataFrame 생성 (각 열이 ETF의 종가)
        price_df = pd.DataFrame(valid_data)
        
        # 공통 날짜만 사용 (한국/미국 ETF 거래일 차이 해결)
        price_df = price_df.dropna()
        
        if len(price_df) < 10:
            raise ValueError(
                f"공통 거래일이 너무 적습니다 ({len(price_df)}일). "
                "한국 ETF와 미국 ETF는 거래일이 달라 상관관계 분석이 어려울 수 있습니다."
            )
        
        # 일일 수익률 계산
        returns_df = price_df.pct_change(fill_method=None).dropna()
        
        if len(returns_df) == 0:
            raise ValueError("수익률 데이터 계산 실패. 데이터가 충분하지 않습니다.")
        
        # 상관관계 매트릭스 계산
        correlation_matrix = returns_df.corr()
        
        # 메타데이터
        metadata = {
            "total_tickers": len(tickers),
            "valid_tickers": list(valid_data.keys()),
            "failed_tickers": failed_tickers,
            "data_points": len(returns_df),
            "period": period,
            "start_date": returns_df.index[0].strftime("%Y-%m-%d") if len(returns_df) > 0 else "N/A",
            "end_date": returns_df.index[-1].strftime("%Y-%m-%d") if len(returns_df) > 0 else "N/A",
            "common_trading_days": len(price_df)
        }
        
        logger.info(f"상관관계 계산 완료: {len(valid_data)}개 종목, {len(returns_df)}개 데이터 포인트")
        
        return correlation_matrix, metadata
    
    @staticmethod
    def analyze_diversification(correlation_matrix: pd.DataFrame) -> Dict:
        """
        분산투자 정도 분석
        
        Args:
            correlation_matrix: 상관관계 매트릭스
        
        Returns:
            분산투자 분석 결과
        """
        logger.info("분산투자 분석 시작")
        
        # 대각선 제외 (자기 자신과의 상관관계 제외)
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=1)
        correlations = correlation_matrix.where(mask).stack()
        
        avg_correlation = float(correlations.mean())
        max_correlation = float(correlations.max())
        min_correlation = float(correlations.min())
        
        # 높은 상관관계 쌍 찾기 (0.7 이상)
        high_corr_pairs = []
        for i in range(len(correlation_matrix)):
            for j in range(i + 1, len(correlation_matrix)):
                corr_value = correlation_matrix.iloc[i, j]
                if corr_value > 0.7:
                    high_corr_pairs.append({
                        "etf1": correlation_matrix.index[i],
                        "etf2": correlation_matrix.columns[j],
                        "correlation": float(corr_value)
                    })
        
        # 분산투자 점수 계산 (0~100)
        # 평균 상관관계가 낮을수록 높은 점수
        # 0.0 상관관계 = 100점, 1.0 상관관계 = 0점
        diversification_score = max(0, min(100, int((1 - avg_correlation) * 100)))
        
        # 평가 및 조언
        if diversification_score >= 80:
            rating = "매우 좋음"
            advice = "포트폴리오가 잘 분산되어 있습니다. 서로 다른 자산군에 투자하고 있어 리스크가 낮습니다."
        elif diversification_score >= 60:
            rating = "좋음"
            advice = "적절한 분산투자가 이루어지고 있습니다. 추가로 다른 섹터나 지역의 ETF를 고려해보세요."
        elif diversification_score >= 40:
            rating = "보통"
            advice = "일부 ETF들이 비슷하게 움직입니다. 채권, 금, 부동산 등 다른 자산군 추가를 권장합니다."
        elif diversification_score >= 20:
            rating = "낮음"
            advice = "⚠️ ETF들이 매우 비슷하게 움직입니다. 진짜 분산투자를 위해 다양한 자산군을 추가하세요."
        else:
            rating = "매우 낮음"
            advice = "🚨 포트폴리오가 거의 같은 방향으로 움직입니다. 분산투자 효과가 거의 없습니다!"
        
        result = {
            "diversification_score": diversification_score,
            "rating": rating,
            "advice": advice,
            "average_correlation": round(avg_correlation, 3),
            "max_correlation": round(max_correlation, 3),
            "min_correlation": round(min_correlation, 3),
            "high_correlation_pairs": high_corr_pairs,
            "total_pairs": len(correlations)
        }
        
        logger.info(f"분산투자 분석 완료: 점수 {diversification_score}, 평균 상관관계 {avg_correlation:.3f}")
        
        return result
    
    @staticmethod
    def create_correlation_heatmap(
        correlation_matrix: pd.DataFrame,
        title: str = "포트폴리오 상관관계 히트맵"
    ) -> str:
        """
        상관관계 히트맵 생성 (Plotly)
        
        Args:
            correlation_matrix: 상관관계 매트릭스
            title: 차트 제목
        
        Returns:
            Plotly JSON
        """
        import plotly.graph_objects as go
        
        logger.info(f"히트맵 생성: {len(correlation_matrix)}x{len(correlation_matrix)}")
        
        # 티커 이름 단순화 (예: 069500.KS -> 069500)
        tickers = [ticker.replace('.KS', '').replace('.KQ', '') for ticker in correlation_matrix.index]
        
        # 히트맵 생성
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=tickers,
            y=tickers,
            colorscale=[
                [0, '#1e3a8a'],      # 낮은 상관관계 (진한 파랑)
                [0.25, '#3b82f6'],   # 낮은~중간 (파랑)
                [0.5, '#fbbf24'],    # 중간 (노랑)
                [0.75, '#f97316'],   # 중간~높은 (주황)
                [1, '#dc2626']       # 높은 상관관계 (빨강)
            ],
            colorbar=dict(
                title=dict(
                    text="상관계수",
                    side="right"
                ),
                tickmode="linear",
                tick0=-1,
                dtick=0.5
            ),
            text=correlation_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False,
            hovertemplate='%{y} vs %{x}<br>상관계수: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#1f2937'}
            },
            xaxis={'title': '', 'side': 'bottom'},
            yaxis={'title': '', 'autorange': 'reversed'},
            width=700,
            height=600,
            margin=dict(l=100, r=100, t=100, b=100),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Pretendard, -apple-system, sans-serif", size=12)
        )
        
        return fig.to_json()

