"""
Vercel Serverless Function Entry Point
"""
from app.main import app

# Vercel은 이 파일을 진입점으로 사용
# FastAPI 앱을 그대로 export
handler = app

