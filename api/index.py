"""
Vercel Serverless Function Entry Point
Vercel이 이 파일을 찾아서 FastAPI 앱을 실행합니다
"""
from app.main import app

# Vercel Python Runtime이 자동으로 'app' 변수를 찾아서 ASGI 서버로 실행
# uvicorn이나 gunicorn 같은 명령어 없이도 작동!

