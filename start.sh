#!/bin/bash
# Gunicorn + Uvicorn worker로 서버 실행

echo "🚀 ETFolio 서버 시작..."
echo "📊 Gunicorn + Uvicorn worker 사용"
echo "🔧 Workers: auto (CPU cores * 2 + 1)"

# 환경 변수 로드
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Gunicorn으로 서버 실행
gunicorn app.main:app \
    --config gunicorn.conf.py \
    --bind 0.0.0.0:8000 \
    --worker-class uvicorn.workers.UvicornWorker

