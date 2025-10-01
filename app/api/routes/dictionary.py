# 주식 용어사전 API 라우트
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.data.stock_terms import STOCK_TERMS, search_terms, get_all_categories, get_terms_by_category
from app.core.logging import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/search")
async def search_stock_terms(q: str, limit: int = 20):
    """
    용어 검색
    
    Args:
        q: 검색어
        limit: 최대 결과 개수
    
    Returns:
        검색 결과
    """
    logger.info(f"용어 검색: '{q}', 제한: {limit}")
    
    try:
        results = search_terms(q, limit)
        logger.info(f"검색 완료: {len(results)}개 결과")
        
        return {
            "query": q,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        logger.error(f"검색 실패: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")


@router.get("/categories")
async def get_all_terms():
    """
    모든 카테고리의 용어 반환
    
    Returns:
        전체 용어 사전
    """
    logger.info("전체 용어 조회")
    
    try:
        return {
            "categories": get_all_categories(),
            "terms": STOCK_TERMS
        }
    except Exception as e:
        logger.error(f"전체 용어 조회 실패: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"용어 조회 실패: {str(e)}")


@router.get("/categories/{category:path}")
async def get_category_terms(category: str):
    """
    특정 카테고리의 용어만 반환
    
    Args:
        category: 카테고리명 (URL 디코딩된 값)
    
    Returns:
        해당 카테고리의 용어들
    """
    # URL 디코딩
    from urllib.parse import unquote
    category = unquote(category)
    
    logger.info(f"카테고리 조회: {category}")
    
    try:
        terms = get_terms_by_category(category)
        
        if not terms:
            # 사용 가능한 카테고리 목록 제공
            available_categories = get_all_categories()
            raise HTTPException(
                status_code=404, 
                detail=f"카테고리 '{category}'를 찾을 수 없습니다. 사용 가능한 카테고리: {available_categories}"
            )
        
        logger.info(f"카테고리 '{category}': {len(terms)}개 용어")
        
        return {
            "category": category,
            "terms": terms,
            "total": len(terms)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"카테고리 조회 실패: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"카테고리 조회 실패: {str(e)}")

