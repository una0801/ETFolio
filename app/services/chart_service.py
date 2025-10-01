"""
Plotly를 활용한 차트 생성 서비스
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict


class ChartService:
    """차트 생성 서비스 클래스"""
    
    @staticmethod
    def create_price_chart(hist: pd.DataFrame, ticker: str) -> Dict:
        """
        가격 추이 차트 생성
        
        Returns:
            Plotly JSON 형식 차트
        """
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist['Close'],
            mode='lines',
            name='종가',
            line=dict(color='#2E86DE', width=2),
            fill='tozeroy',
            fillcolor='rgba(46, 134, 222, 0.1)'
        ))
        
        fig.update_layout(
            title=f'{ticker} 가격 추이',
            xaxis_title='날짜',
            yaxis_title='가격',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_dividend_chart(dividends, ticker: str) -> Dict:
        """
        배당금 차트 생성
        
        Returns:
            Plotly JSON 형식 차트
        """
        # dividends가 list이거나 None인 경우 빈 Series로 변환
        if isinstance(dividends, list) or dividends is None:
            dividends = pd.Series(dtype=float)
        
        if dividends.empty:
            # 빈 차트 반환
            fig = go.Figure()
            fig.update_layout(
                title=f'{ticker} 배당금 내역',
                annotations=[{
                    'text': '배당 데이터가 없습니다',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 16}
                }]
            )
            return fig.to_json()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=dividends.index,
            y=dividends.values,
            name='배당금',
            marker_color='#26DE81'
        ))
        
        fig.update_layout(
            title=f'{ticker} 배당금 내역',
            xaxis_title='날짜',
            yaxis_title='배당금',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_portfolio_pie_chart(holdings: list) -> Dict:
        """
        포트폴리오 비중 파이 차트 생성
        
        Args:
            holdings: [{"name": str, "value": float}, ...]
        
        Returns:
            Plotly JSON 형식 차트
        """
        if not holdings:
            fig = go.Figure()
            fig.update_layout(
                title='포트폴리오 구성',
                annotations=[{
                    'text': '포트폴리오 데이터가 없습니다',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 16}
                }]
            )
            return fig.to_json()
        
        labels = [h['name'] for h in holdings]
        values = [h['value'] for h in holdings]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker=dict(colors=px.colors.qualitative.Set3)
        )])
        
        fig.update_layout(
            title='포트폴리오 구성 비중',
            template='plotly_white',
            height=400
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_cumulative_return_chart(hist: pd.DataFrame, ticker: str) -> Dict:
        """
        누적 수익률 차트 생성
        
        Returns:
            Plotly JSON 형식 차트
        """
        # 누적 수익률 계산
        initial_price = hist['Close'].iloc[0]
        cumulative_return = ((hist['Close'] - initial_price) / initial_price) * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=cumulative_return,
            mode='lines',
            name='누적 수익률',
            line=dict(color='#FC427B', width=2),
            fill='tozeroy',
            fillcolor='rgba(252, 66, 123, 0.1)'
        ))
        
        fig.update_layout(
            title=f'{ticker} 누적 수익률',
            xaxis_title='날짜',
            yaxis_title='수익률 (%)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig.to_json()

