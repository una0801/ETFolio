# 배포 가이드

ETFolio를 다양한 환경에 배포하는 방법을 안내합니다.

## 🚀 로컬 개발 환경

### 기본 실행 (개발용)
```bash
# Uvicorn만 사용 (단일 워커, 핫 리로드)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Gunicorn + Uvicorn Worker (프로덕션 로컬 테스트)
```bash
# 방법 1: 스크립트 사용
chmod +x start.sh
./start.sh

# 방법 2: 직접 실행
gunicorn app.main:app \
    --config gunicorn.conf.py \
    --bind 0.0.0.0:8000 \
    --worker-class uvicorn.workers.UvicornWorker
```

### Worker 설정
`gunicorn.conf.py` 파일에서 worker 수를 조정할 수 있습니다:
- **기본값**: `(CPU 코어 수 * 2) + 1`
- **개발 환경**: 2-4 workers
- **프로덕션**: CPU 코어 수에 따라 자동 조정

## ☁️ Vercel 배포

Vercel은 serverless 환경이므로 Gunicorn을 직접 사용하지 않고, FastAPI를 serverless function으로 변환합니다.

### 1. Vercel CLI 설치
```bash
npm install -g vercel
```

### 2. Vercel 프로젝트 초기화
```bash
vercel login
vercel
```

### 3. 환경 변수 설정
Vercel 대시보드에서 환경 변수를 설정하거나 CLI로 설정:
```bash
vercel env add DATABASE_URL
vercel env add APP_NAME
```

### 4. 배포
```bash
# 프리뷰 배포
vercel

# 프로덕션 배포
vercel --prod
```

### Vercel 배포 시 주의사항
1. **데이터베이스**: SQLite는 Vercel에서 제한적입니다. PostgreSQL 사용 권장
2. **Serverless 제약**: 각 요청은 독립적인 함수로 실행됩니다
3. **정적 파일**: `static/` 폴더는 자동으로 CDN에 배포됩니다
4. **Timeout**: 기본 10초 제한 (Pro: 60초)

### PostgreSQL로 전환 (Vercel 권장)
```python
# .env
DATABASE_URL=postgresql://user:password@host:5432/dbname

# requirements.txt에 추가
psycopg2-binary==2.9.9
```

## 🐳 Docker 배포

### Dockerfile 생성
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "--config", "gunicorn.conf.py"]
```

### Docker 실행
```bash
# 이미지 빌드
docker build -t etfolio .

# 컨테이너 실행
docker run -d -p 8000:8000 --name etfolio etfolio
```

## 🌐 일반 서버 (Ubuntu/Debian)

### 1. 시스템 준비
```bash
sudo apt update
sudo apt install python3.11 python3-pip nginx
```

### 2. 프로젝트 설정
```bash
cd /var/www/etfolio
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Systemd 서비스 생성
```bash
sudo nano /etc/systemd/system/etfolio.service
```

```ini
[Unit]
Description=ETFolio FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/etfolio
Environment="PATH=/var/www/etfolio/venv/bin"
ExecStart=/var/www/etfolio/venv/bin/gunicorn app.main:app \
    --config /var/www/etfolio/gunicorn.conf.py

[Install]
WantedBy=multi-user.target
```

### 4. Nginx 설정
```bash
sudo nano /etc/nginx/sites-available/etfolio
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /var/www/etfolio/static;
    }
}
```

### 5. 서비스 시작
```bash
sudo systemctl enable etfolio
sudo systemctl start etfolio
sudo systemctl enable nginx
sudo systemctl restart nginx
```

## 📊 성능 최적화

### Worker 수 조정
```python
# gunicorn.conf.py
workers = multiprocessing.cpu_count() * 2 + 1

# 메모리가 부족한 경우
workers = multiprocessing.cpu_count()

# 높은 I/O 부하가 예상되는 경우
workers = multiprocessing.cpu_count() * 3
```

### Connection Pooling
현재 SQLite의 `StaticPool`을 사용하고 있습니다. PostgreSQL 사용 시:
```python
# app/core/database.py
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,          # 기본 연결 풀 크기
    max_overflow=10,       # 최대 초과 연결 수
    pool_pre_ping=True,
)
```

## 🔒 보안 설정

### 환경 변수 (프로덕션)
```bash
# .env
DEBUG=False
ALLOWED_HOSTS=["your-domain.com"]
SECRET_KEY=your-secret-key-here
```

### HTTPS 설정 (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📈 모니터링

### 로그 확인
```bash
# Systemd 서비스
journalctl -u etfolio -f

# Gunicorn 로그
tail -f /var/log/gunicorn/access.log
tail -f /var/log/gunicorn/error.log
```

### 성능 모니터링 도구
- **Prometheus + Grafana**: 메트릭 수집 및 시각화
- **Sentry**: 에러 트래킹
- **New Relic**: APM 모니터링

## 🔄 무중단 배포

Gunicorn의 graceful restart 기능 활용:
```bash
# 기존 연결 유지하며 재시작
kill -HUP $(cat /var/run/gunicorn.pid)

# Systemd 사용 시
sudo systemctl reload etfolio
```

## 📝 체크리스트

배포 전 확인사항:
- [ ] 환경 변수 설정 완료
- [ ] 데이터베이스 마이그레이션
- [ ] 정적 파일 경로 확인
- [ ] CORS 설정 확인
- [ ] 로그 디렉토리 권한 확인
- [ ] SSL 인증서 설정 (HTTPS)
- [ ] 방화벽 설정
- [ ] 백업 설정

## 🆘 문제 해결

### Worker가 제대로 시작되지 않는 경우
```bash
# 로그 확인
gunicorn app.main:app --log-level debug

# Worker 수 줄이기
workers = 2
```

### Vercel에서 timeout 발생
- yfinance 호출이 느릴 수 있습니다. 캐싱 추가 권장
- Vercel Pro 플랜으로 업그레이드 (60초 timeout)

### 메모리 부족
- Worker 수 줄이기
- `max_requests` 설정으로 주기적으로 worker 재시작

---

**문의사항이 있으시면 이슈를 등록해주세요!**

