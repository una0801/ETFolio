"""
ETFolio - ETF 포트폴리오 트래커 메인 애플리케이션
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import etf, portfolio

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ETF 포트폴리오 트래커 - 수익률, 배당금, 분석 대시보드"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
static_path = Path(__file__).parent.parent / "static"
templates_path = Path(__file__).parent.parent / "templates"

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# API 라우터 등록
app.include_router(etf.router, prefix=settings.API_V1_STR)
app.include_router(portfolio.router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def startup_event():
    """애플리케이션 시작 시 실행"""
    # 데이터베이스 초기화
    init_db()
    print("📊 ETFolio 시작!")
    print(f"📍 API 문서: http://localhost:8000/docs")


@app.get("/", response_class=HTMLResponse)
async def root():
    """메인 페이지"""
    index_file = templates_path / "index.html"
    
    if index_file.exists():
        return index_file.read_text(encoding='utf-8')
    
    # 기본 환영 메시지
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ETFolio</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>📈 ETFolio에 오신 것을 환영합니다!</h1>
        <p>ETF 포트폴리오 트래커입니다.</p>
        <ul>
            <li><a href="/docs">API 문서 보기</a></li>
            <li><a href="/api/v1/etf">ETF 목록</a></li>
            <li><a href="/api/v1/portfolio/summary">포트폴리오 요약</a></li>
        </ul>
    </body>
    </html>
    """


@app.get("/health")
def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/api/v1/db-info")
def get_db_info():
    """현재 데이터베이스 연결 정보"""
    from app.core.database import db_url, is_postgres
    
    # URL에서 비밀번호 숨기기
    safe_url = db_url
    if "@" in db_url:
        # postgresql://user:password@host:port/db -> postgresql://user:***@host:port/db
        parts = db_url.split("@")
        if ":" in parts[0]:
            user_part = parts[0].split(":")
            safe_url = f"{user_part[0]}:***@{parts[1]}"
    
    return {
        "database_type": "PostgreSQL" if is_postgres else "SQLite",
        "is_production": is_postgres,
        "connection_url": safe_url,
        "environment": "Production (Vercel)" if is_postgres else "Development (Local)",
        "status": "connected"
    }

