"""
Gunicorn 설정 파일
Uvicorn worker를 사용한 비동기 처리
"""
import multiprocessing

# 서버 소켓
bind = "0.0.0.0:8000"
backlog = 2048

# Worker 프로세스
workers = multiprocessing.cpu_count() * 2 + 1  # 권장: (CPU 코어 수 * 2) + 1
worker_class = "uvicorn.workers.UvicornWorker"  # Uvicorn worker 사용
worker_connections = 1000
max_requests = 1000  # 메모리 누수 방지를 위해 주기적으로 worker 재시작
max_requests_jitter = 50  # 랜덤성 추가

# 타임아웃
timeout = 120
keepalive = 5

# 로깅
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 프로세스 이름
proc_name = "etfolio"

# Graceful timeout
graceful_timeout = 30

# Development vs Production
# import os
# if os.getenv("ENV") == "production":
#     workers = multiprocessing.cpu_count() * 2 + 1
#     loglevel = "warning"
# else:
#     workers = 2
#     loglevel = "debug"

