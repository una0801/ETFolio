# ETFolio

ETF 포트폴리오 트래커 - 내 ETF 투자를 한눈에

## 프로젝트 소개

ETFolio는 개인 투자자를 위한 ETF 포트폴리오 관리 및 분석 대시보드입니다.
yfinance와 FinanceDataReader를 활용하여 실시간 ETF 데이터를 가져오고, 수익률, 배당금, 위험 지표 등을 시각화합니다.

### 주요 기능

**ETF 관리**
- 실시간 ETF 목록 조회 (한국 ETF 1029개 + 미국 주요 ETF)
- 검색 가능한 드롭다운으로 ETF 선택
- yfinance를 통한 실시간 가격 및 배당금 정보

**투자 분석**
- 총 수익률 (Total Return)
- 연평균 복리 수익률 (CAGR)
- 변동성 (Volatility)
- 샤프 비율 (Sharpe Ratio)
- 최대 낙폭 (Maximum Drawdown)
- 배당 수익률 (Dividend Yield)

**포트폴리오 상관관계 분석** (신규)
- ETF 간 상관관계 히트맵
- 분산투자 점수 계산 (0~100점)
- 한국 ETF / 미국 ETF 자동 그룹화
- 높은 상관관계 ETF 쌍 자동 감지
- 분산투자 개선 조언

**시각화**
- Plotly 기반 인터랙티브 차트
- 가격 추이 차트
- 배당금 차트
- 누적 수익률 차트
- 상관관계 히트맵

**UI/UX**
- 다크 모드 프로페셔널 디자인
- 반응형 레이아웃
- 데이터베이스 연결 정보 모달

## 기술 스택

**Backend**
- FastAPI (비동기 처리)
- SQLAlchemy ORM
- PostgreSQL (Production) / SQLite (Development)

**Data Source**
- yfinance (가격, 배당금 데이터)
- FinanceDataReader (ETF 목록 수집)

**Visualization**
- Plotly (인터랙티브 차트)

**Frontend**
- HTML/CSS/JavaScript (Vanilla)
- Choices.js (검색 가능한 드롭다운)

**Deployment**
- Gunicorn + Uvicorn Workers
- Vercel (Serverless)

## 설치 및 실행

### 1. 저장소 클론

```bash
git clone https://github.com/una0801/ETFolio.git
cd ETFolio
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정 (선택사항)

PostgreSQL을 사용하려면 `.env` 파일 생성:

```bash
POSTGRES_URL=postgresql://user:password@host:port/database
```

### 5. 애플리케이션 실행

**개발 환경 (단일 워커, 핫 리로드)**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**프로덕션 환경 (Gunicorn + Uvicorn Worker)**
```bash
# 방법 1: 스크립트 사용
chmod +x start.sh
./start.sh

# 방법 2: 직접 실행
gunicorn app.main:app --config gunicorn.conf.py
```

애플리케이션이 `http://localhost:8000` 에서 실행됩니다.

- 메인 대시보드: http://localhost:8000
- API 문서: http://localhost:8000/docs
- 헬스 체크: http://localhost:8000/health
- DB 정보: http://localhost:8000/api/v1/db-info

### 6. Vercel 배포

상세한 배포 가이드는 [VERCEL_SETUP.md](VERCEL_SETUP.md)를 참고하세요.

```bash
vercel
```

## 프로젝트 구조

```
ETFolio/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI 메인 애플리케이션
│   ├── api/
│   │   └── routes/
│   │       ├── etf.py               # ETF 관련 API 엔드포인트
│   │       └── portfolio.py         # 포트폴리오 관련 API 엔드포인트
│   ├── core/
│   │   ├── config.py                # 설정 (PostgreSQL/SQLite 자동 전환)
│   │   ├── database.py              # 데이터베이스 연결 (Connection Pool)
│   │   └── logging.py               # 로깅 설정
│   ├── models/
│   │   └── etf.py                   # SQLAlchemy 모델
│   ├── schemas/
│   │   └── etf.py                   # Pydantic 스키마
│   ├── services/
│   │   ├── yfinance_service.py      # yfinance 데이터 조회
│   │   ├── analytics_service.py     # 투자 분석 로직
│   │   ├── chart_service.py         # Plotly 차트 생성
│   │   ├── etf_list_service.py      # ETF 목록 수집 (FinanceDataReader)
│   │   └── correlation_service.py   # 상관관계 분석
│   └── data/
│       └── __init__.py
├── api/
│   └── index.py                     # Vercel 서버리스 엔트리포인트
├── static/
│   ├── css/
│   │   └── style.css                # 다크 테마 스타일시트
│   └── js/
│       └── app.js                   # 프론트엔드 JavaScript
├── templates/
│   └── index.html                   # 메인 HTML
├── logs/                            # 로그 파일 (로컬 환경만)
├── requirements.txt                 # Python 패키지 목록
├── gunicorn.conf.py                 # Gunicorn 설정
├── vercel.json                      # Vercel 배포 설정
├── README.md
├── DEPLOYMENT.md                    # 배포 가이드
└── VERCEL_SETUP.md                  # Vercel 배포 상세 가이드
```

## 사용 방법

### ETF 추가하기

1. 드롭다운에서 ETF 검색 (1000개 이상 제공)
   - 한국 ETF: KODEX, TIGER, KBSTAR, ARIRANG 등
   - 미국 ETF: SPY, QQQ, VOO, VTI 등
2. 검색창에 종목명 또는 티커 입력
3. 선택 후 "추가" 버튼 클릭

### 포트폴리오 분석

**개별 ETF 분석**
1. ETF 선택 드롭다운에서 분석할 ETF 선택
2. 기간 선택 (1개월 ~ 5년)
3. "차트 보기" 버튼 클릭
4. 수익률, 배당금, 누적 수익률 차트 확인

**상관관계 분석**
1. 2개 이상의 ETF 추가
2. "포트폴리오 상관관계 분석" 섹션으로 스크롤
3. 분석 기간 선택
4. "상관관계 분석" 버튼 클릭
5. 결과 확인:
   - 분산투자 점수 (0~100점)
   - 상관관계 히트맵
   - 높은 상관관계 ETF 쌍 경고
   - 분산투자 개선 조언

## API 엔드포인트

### ETF 관련
- `POST /api/v1/etf/`: ETF 추가
- `GET /api/v1/etf/`: ETF 목록 조회
- `GET /api/v1/etf/list`: 사용 가능한 ETF 목록 (검색, 페이지네이션 지원)
- `GET /api/v1/etf/{ticker}/analytics`: ETF 분석 정보
- `GET /api/v1/etf/{ticker}/chart/price`: 가격 차트
- `GET /api/v1/etf/{ticker}/chart/dividend`: 배당금 차트
- `GET /api/v1/etf/{ticker}/chart/cumulative-return`: 누적 수익률 차트
- `DELETE /api/v1/etf/{ticker}`: ETF 삭제

### 포트폴리오 관련
- `POST /api/v1/portfolio/holding`: 보유 ETF 추가
- `GET /api/v1/portfolio/holdings`: 보유 ETF 목록
- `GET /api/v1/portfolio/summary`: 포트폴리오 요약
- `GET /api/v1/portfolio/chart/allocation`: 자산 배분 차트
- `GET /api/v1/portfolio/correlation`: 포트폴리오 상관관계 분석 (신규)

### 시스템
- `GET /health`: 헬스 체크
- `GET /api/v1/db-info`: 데이터베이스 연결 정보

## 배울 수 있는 투자 개념

**수익률 지표**
- CAGR (연평균 복리 수익률): 장기 투자 성과 측정
- 총 수익률: 전체 투자 기간 수익률

**위험 지표**
- 변동성 (Volatility): 가격 변동 폭 (리스크 지표)
- 최대 낙폭 (MDD): 최고점 대비 최대 하락률
- 샤프 비율 (Sharpe Ratio): 위험 대비 수익률 (높을수록 좋음)

**배당**
- 배당 수익률: 주가 대비 배당금 비율

**포트폴리오 분석**
- 상관관계: ETF 간 가격 움직임의 유사도 (-1.0 ~ 1.0)
- 분산투자 효과: 낮은 상관관계 = 높은 분산투자 효과

## 기술적 특징

**비동기 처리**
- FastAPI의 async/await 활용
- asyncio.to_thread로 blocking I/O 처리
- asyncio.gather로 병렬 데이터 수집

**데이터베이스**
- SQLite (로컬 개발)
- PostgreSQL (Vercel 배포)
- Connection Pooling (QueuePool)
- 자동 전환 (환경 변수 기반)

**캐싱**
- ETF 목록 24시간 캐싱
- 메모리 캐시로 성능 최적화

**로깅**
- 구조화된 로깅 (콘솔 + 파일)
- 에러 추적 (exc_info=True)
- Vercel 환경 자동 감지

## 확장 아이디어

- [ ] 포트폴리오 리밸런싱 계산기
- [ ] 배당 캘린더 및 예상 수익
- [ ] 백테스팅 시뮬레이터
- [ ] ISA 세금 계산기
- [ ] 월간 투자 리포트 (PDF 생성)
- [ ] 알림 기능 (목표가 도달 시)
- [ ] 다중 포트폴리오 관리
- [ ] 엑셀 내보내기
- [ ] 모바일 반응형 개선

## 참고사항

**데이터 제한**
- yfinance 데이터는 15~20분 지연될 수 있습니다
- 한국 ETF는 `.KS` 또는 `.KQ` 접미사가 필요합니다
- 일부 ETF는 데이터가 제한적일 수 있습니다

**상관관계 분석**
- 한국 ETF와 미국 ETF는 거래일이 달라 별도 그룹으로 분석됩니다
- 같은 시장의 ETF 2개 이상 필요
- 공통 거래일 10일 이상 필요

**성능**
- 첫 ETF 목록 로딩: 약 2~3초 (캐싱 후 즉시)
- 상관관계 분석: ETF당 1~2초 (병렬 처리)

## 라이선스

이 프로젝트는 개인 학습 및 포트폴리오 목적으로 제작되었습니다.

---

Made for ISA Investors
