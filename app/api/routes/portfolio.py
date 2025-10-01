"""
포트폴리오 관련 API 라우트
비동기 처리로 여러 사용자의 동시 요청 처리
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.database import get_db
from app.core.logging import setup_logger
from app.models.etf import Holding, ETF
from app.schemas.etf import HoldingCreate, HoldingResponse, PortfolioSummary
from app.services.yfinance_service import YFinanceService
from app.services.chart_service import ChartService
from app.services.correlation_service import CorrelationService
from app.services.recommendation_service import RecommendationService

logger = setup_logger(__name__)

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

# ThreadPoolExecutor for blocking I/O operations
executor = ThreadPoolExecutor(max_workers=10)


@router.post("/holding", response_model=HoldingResponse)
async def add_holding(holding: HoldingCreate, db: Session = Depends(get_db)):
    """포트폴리오에 보유 ETF 추가 (비동기)"""
    loop = asyncio.get_event_loop()
    
    # ETF 존재 확인
    etf = await loop.run_in_executor(
        executor, lambda: db.query(ETF).filter(ETF.id == holding.etf_id).first()
    )
    if not etf:
        raise HTTPException(status_code=404, detail="ETF를 찾을 수 없습니다")
    
    # 보유 정보 저장
    db_holding = Holding(**holding.dict())
    await loop.run_in_executor(
        executor, lambda: (db.add(db_holding), db.commit(), db.refresh(db_holding))
    )
    
    return db_holding


@router.get("/holdings", response_model=List[HoldingResponse])
async def get_holdings(db: Session = Depends(get_db)):
    """모든 보유 ETF 조회 (비동기)"""
    loop = asyncio.get_event_loop()
    holdings = await loop.run_in_executor(
        executor, lambda: db.query(Holding).all()
    )
    return holdings


@router.get("/summary")
async def get_portfolio_summary(db: Session = Depends(get_db)):
    """포트폴리오 요약 정보 (비동기)"""
    loop = asyncio.get_event_loop()
    holdings = await loop.run_in_executor(
        executor, lambda: db.query(Holding).all()
    )
    
    if not holdings:
        return {
            "total_investment": 0,
            "current_value": 0,
            "total_return": 0,
            "return_rate": 0,
            "total_dividends": 0,
            "holdings": []
        }
    
    total_investment = 0
    current_value = 0
    total_dividends = 0
    
    # 병렬로 각 ETF의 가격 및 배당금 조회
    price_tasks = []
    dividend_tasks = []
    
    for holding in holdings:
        price_tasks.append(
            loop.run_in_executor(
                executor, YFinanceService.get_current_price, holding.etf.ticker
            )
        )
        dividend_tasks.append(
            loop.run_in_executor(
                executor, YFinanceService.get_dividends, holding.etf.ticker
            )
        )
    
    # 모든 요청을 병렬로 실행
    prices = await asyncio.gather(*price_tasks)
    dividends_list = await asyncio.gather(*dividend_tasks)
    
    for idx, holding in enumerate(holdings):
        # 투자 금액
        investment = holding.quantity * holding.average_price
        total_investment += investment
        
        # 현재 가격
        current_price = prices[idx]
        if current_price:
            current_value += holding.quantity * current_price
        
        # 배당금
        dividends = dividends_list[idx]
        if dividends is not None:
            # 보유 기간 동안의 배당금만 계산
            period_dividends = dividends[dividends.index >= holding.purchase_date]
            total_dividends += period_dividends.sum() * holding.quantity
    
    total_return = current_value - total_investment
    return_rate = (total_return / total_investment * 100) if total_investment > 0 else 0
    
    return {
        "total_investment": round(total_investment, 2),
        "current_value": round(current_value, 2),
        "total_return": round(total_return, 2),
        "return_rate": round(return_rate, 2),
        "total_dividends": round(total_dividends, 2),
        "holdings": holdings
    }


@router.get("/chart/allocation")
async def get_allocation_chart(db: Session = Depends(get_db)):
    """포트폴리오 자산 배분 차트 (비동기)"""
    loop = asyncio.get_event_loop()
    holdings = await loop.run_in_executor(
        executor, lambda: db.query(Holding).all()
    )
    
    if not holdings:
        raise HTTPException(status_code=404, detail="보유 중인 ETF가 없습니다")
    
    # 병렬로 각 ETF의 현재 가격 조회
    price_tasks = [
        loop.run_in_executor(
            executor, YFinanceService.get_current_price, holding.etf.ticker
        )
        for holding in holdings
    ]
    prices = await asyncio.gather(*price_tasks)
    
    # 각 ETF의 현재 가치 계산
    portfolio_data = []
    for idx, holding in enumerate(holdings):
        current_price = prices[idx]
        if current_price:
            value = holding.quantity * current_price
            portfolio_data.append({
                "name": f"{holding.etf.name} ({holding.etf.ticker})",
                "value": value
            })
    
    chart = await loop.run_in_executor(
        executor, ChartService.create_portfolio_pie_chart, portfolio_data
    )
    return {"chart": chart}


@router.put("/holding/{holding_id}")
async def update_holding(
    holding_id: int,
    quantity: float = None,
    average_price: float = None,
    db: Session = Depends(get_db)
):
    """보유 ETF 정보 수정 (비동기)"""
    loop = asyncio.get_event_loop()
    holding = await loop.run_in_executor(
        executor, lambda: db.query(Holding).filter(Holding.id == holding_id).first()
    )
    
    if not holding:
        raise HTTPException(status_code=404, detail="보유 정보를 찾을 수 없습니다")
    
    if quantity is not None:
        holding.quantity = quantity
    if average_price is not None:
        holding.average_price = average_price
    
    await loop.run_in_executor(
        executor, lambda: (db.commit(), db.refresh(holding))
    )
    
    return holding


@router.delete("/holding/{holding_id}")
async def delete_holding(holding_id: int, db: Session = Depends(get_db)):
    """보유 ETF 삭제 (비동기)"""
    loop = asyncio.get_event_loop()
    holding = await loop.run_in_executor(
        executor, lambda: db.query(Holding).filter(Holding.id == holding_id).first()
    )
    
    if not holding:
        raise HTTPException(status_code=404, detail="보유 정보를 찾을 수 없습니다")
    
    await loop.run_in_executor(
        executor, lambda: (db.delete(holding), db.commit())
    )
    
    return {"message": "보유 정보가 삭제되었습니다"}


@router.get("/correlation")
async def get_portfolio_correlation(
    period: str = "1y",
    db: Session = Depends(get_db)
):
    """
    포트폴리오 상관관계 분석 (비동기)
    - 한국 ETF와 미국 ETF를 자동으로 그룹화하여 각각 분석
    
    Args:
        period: 분석 기간 (1mo, 3mo, 6mo, 1y, 2y, 5y)
    
    Returns:
        그룹별 상관관계 분석 결과
    """
    logger.info(f"포트폴리오 상관관계 분석 요청: 기간={period}")
    
    try:
        # 등록된 모든 ETF 조회
        etfs = await asyncio.to_thread(lambda: db.query(ETF).all())
        
        if len(etfs) == 0:
            raise HTTPException(
                status_code=400,
                detail="등록된 ETF가 없습니다. ETF를 추가해주세요."
            )
        
        # 한국 ETF와 미국 ETF 분리
        korean_etfs = [etf for etf in etfs if etf.ticker.endswith('.KS') or etf.ticker.endswith('.KQ')]
        us_etfs = [etf for etf in etfs if not (etf.ticker.endswith('.KS') or etf.ticker.endswith('.KQ'))]
        
        logger.info(f"분석 대상: 한국 {len(korean_etfs)}개, 미국 {len(us_etfs)}개")
        
        results = {
            "groups": [],
            "total_etfs": len(etfs),
            "period": period
        }
        
        # 한국 ETF 분석
        if len(korean_etfs) >= 2:
            korean_tickers = [etf.ticker for etf in korean_etfs]
            try:
                correlation_matrix, metadata = await CorrelationService.calculate_correlation_matrix(
                    korean_tickers, period
                )
                diversification = CorrelationService.analyze_diversification(correlation_matrix)
                heatmap = CorrelationService.create_correlation_heatmap(
                    correlation_matrix,
                    title=f"한국 ETF 상관관계 ({period})"
                )
                
                results["groups"].append({
                    "name": "한국 ETF",
                    "etf_count": len(korean_etfs),
                    "etf_names": [etf.name for etf in korean_etfs],
                    "correlation_matrix": correlation_matrix.to_dict(),
                    "heatmap": heatmap,
                    "diversification": diversification,
                    "metadata": metadata
                })
                logger.info(f"한국 ETF 분석 완료: {len(korean_etfs)}개")
            except Exception as e:
                logger.error(f"한국 ETF 분석 실패: {str(e)}")
                results["groups"].append({
                    "name": "한국 ETF",
                    "etf_count": len(korean_etfs),
                    "error": str(e)
                })
        elif len(korean_etfs) == 1:
            results["groups"].append({
                "name": "한국 ETF",
                "etf_count": 1,
                "etf_names": [korean_etfs[0].name],
                "message": "비교 대상이 없습니다. 한국 ETF를 1개 더 추가하면 상관관계를 분석할 수 있습니다."
            })
        
        # 미국 ETF 분석
        if len(us_etfs) >= 2:
            us_tickers = [etf.ticker for etf in us_etfs]
            try:
                correlation_matrix, metadata = await CorrelationService.calculate_correlation_matrix(
                    us_tickers, period
                )
                diversification = CorrelationService.analyze_diversification(correlation_matrix)
                heatmap = CorrelationService.create_correlation_heatmap(
                    correlation_matrix,
                    title=f"미국 ETF 상관관계 ({period})"
                )
                
                results["groups"].append({
                    "name": "미국 ETF",
                    "etf_count": len(us_etfs),
                    "etf_names": [etf.name for etf in us_etfs],
                    "correlation_matrix": correlation_matrix.to_dict(),
                    "heatmap": heatmap,
                    "diversification": diversification,
                    "metadata": metadata
                })
                logger.info(f"미국 ETF 분석 완료: {len(us_etfs)}개")
            except Exception as e:
                logger.error(f"미국 ETF 분석 실패: {str(e)}")
                results["groups"].append({
                    "name": "미국 ETF",
                    "etf_count": len(us_etfs),
                    "error": str(e)
                })
        elif len(us_etfs) == 1:
            results["groups"].append({
                "name": "미국 ETF",
                "etf_count": 1,
                "etf_names": [us_etfs[0].name],
                "message": "비교 대상이 없습니다. 미국 ETF를 1개 더 추가하면 상관관계를 분석할 수 있습니다."
            })
        
        if len(results["groups"]) == 0:
            raise HTTPException(
                status_code=400,
                detail="분석 가능한 ETF 그룹이 없습니다. 같은 시장의 ETF를 2개 이상 추가해주세요."
            )
        
        logger.info(f"상관관계 분석 완료: {len(results['groups'])}개 그룹")
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"상관관계 분석 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"상관관계 분석 실패: {str(e)}")


@router.get("/recommendations")
async def get_etf_recommendations(
    category: str = "all",
    period: str = "5y",
    limit: int = 5
):
    """
    인기 ETF 추천 (성과 기준)
    
    Args:
        category: 카테고리 필터 (korean, us, all)
        period: 분석 기간 (1y, 3y, 5y)
        limit: 카테고리별 추천 개수
    
    Returns:
        카테고리별 추천 ETF 목록
    """
    logger.info(f"ETF 추천 요청: category={category}, period={period}, limit={limit}")
    try:
        from app.services.recommendation_service import RecommendationService
        
        recommendations = await RecommendationService.get_recommended_etfs(
            category_filter=category,
            period=period,
            limit=limit
        )
        logger.info(f"ETF 추천 완료: {recommendations['metadata']['total_analyzed']}개 ETF 분석")
        return recommendations
    except Exception as e:
        logger.error(f"ETF 추천 실패: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ETF 추천 실패: {str(e)}")

