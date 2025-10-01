"""
API 테스트
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """헬스 체크 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_etfs():
    """ETF 목록 조회 테스트"""
    response = client.get("/api/v1/etf/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_portfolio_summary():
    """포트폴리오 요약 테스트"""
    response = client.get("/api/v1/portfolio/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_investment" in data
    assert "current_value" in data
    assert "total_return" in data

