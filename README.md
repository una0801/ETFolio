# 📈 ETFolio

**ETF 포트폴리오 트래커** - 내 ETF 투자를 한눈에!

## 🎯 프로젝트 소개

ETFolio는 개인 투자자를 위한 ETF 포트폴리오 관리 및 분석 대시보드입니다.
yfinance를 활용하여 실시간 ETF 데이터를 가져오고, 수익률, 배당금, 위험 지표 등을 시각화합니다.

### 주요 기능

- 📊 **ETF 데이터 조회**: yfinance를 통한 실시간 가격 및 배당금 정보
- 💰 **포트폴리오 관리**: 보유 ETF 추적 및 수익률 계산
- 📉 **투자 분석**:
  - 총 수익률 (Total Return)
  - 연평균 복리 수익률 (CAGR)
  - 변동성 (Volatility)
  - 샤프 비율 (Sharpe Ratio)
  - 최대 낙폭 (Maximum Drawdown)
  - 배당 수익률 (Dividend Yield)
- 📈 **인터랙티브 차트**: Plotly 기반 동적 차트
- 🇰🇷 **한국 ETF 지원**: KODEX, TIGER 등 한국 ETF 빠른 조회

## 🛠 기술 스택

- **Backend**: FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **Data Source**: yfinance
- **Visualization**: Plotly
- **Frontend**: HTML/CSS/JavaScript (Vanilla)

## 📦 설치 및 실행

### 1. 저장소 클론

```bash
git clone <repository-url>
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

### 4. 애플리케이션 실행

#### 개발 환경 (단일 워커, 핫 리로드)
```bash
uvicorn app.main:app --reload
```

#### 프로덕션 환경 (Gunicorn + Uvicorn Worker)
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

### 5. Vercel 배포

상세한 배포 가이드는 [DEPLOYMENT.md](DEPLOYMENT.md)를 참고하세요.

```bash
vercel
```

## 📁 프로젝트 구조

```
ETFolio/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 메인 애플리케이션
│   ├── api/
│   │   └── routes/
│   │       ├── etf.py          # ETF 관련 API 엔드포인트
│   │       └── portfolio.py    # 포트폴리오 관련 API 엔드포인트
│   ├── core/
│   │   ├── config.py           # 설정
│   │   └── database.py         # 데이터베이스 연결
│   ├── models/
│   │   └── etf.py              # SQLAlchemy 모델
│   ├── schemas/
│   │   └── etf.py              # Pydantic 스키마
│   └── services/
│       ├── yfinance_service.py # yfinance 데이터 조회
│       ├── analytics_service.py # 투자 분석 로직
│       └── chart_service.py    # Plotly 차트 생성
├── static/
│   ├── css/
│   │   └── style.css           # 스타일시트
│   └── js/
│       └── app.js              # 프론트엔드 JavaScript
├── templates/
│   └── index.html              # 메인 HTML
├── tests/
│   └── __init__.py
├── requirements.txt            # Python 패키지 목록
├── README.md
└── .gitignore
```

## 🚀 사용 방법

### ETF 추가하기

1. 메인 페이지에서 종목 코드와 이름을 입력
2. 또는 "빠른 추가" 버튼으로 인기 ETF 추가
   - KODEX 200: `069500.KS`
   - KODEX S&P500: `360750.KS`
   - TIGER 미국배당귀족: `458730.KS`
   - TIGER 미국나스닥100: `133690.KS`

### 포트폴리오 분석

1. ETF 선택 드롭다운에서 분석할 ETF 선택
2. 기간 선택 (1개월 ~ 5년)
3. "차트 보기" 버튼 클릭
4. 수익률, 배당금, 누적 수익률 차트 확인

## 📊 API 엔드포인트

### ETF 관련
- `POST /api/v1/etf/`: ETF 추가
- `GET /api/v1/etf/`: ETF 목록 조회
- `GET /api/v1/etf/{ticker}/info`: ETF 정보 조회
- `GET /api/v1/etf/{ticker}/analytics`: ETF 분석 정보
- `GET /api/v1/etf/{ticker}/chart/price`: 가격 차트
- `GET /api/v1/etf/{ticker}/chart/dividend`: 배당금 차트
- `DELETE /api/v1/etf/{ticker}`: ETF 삭제

### 포트폴리오 관련
- `POST /api/v1/portfolio/holding`: 보유 ETF 추가
- `GET /api/v1/portfolio/holdings`: 보유 ETF 목록
- `GET /api/v1/portfolio/summary`: 포트폴리오 요약
- `GET /api/v1/portfolio/chart/allocation`: 자산 배분 차트

## 🎓 배울 수 있는 투자 개념

- **CAGR (연평균 복리 수익률)**: 장기 투자 성과 측정
- **샤프 비율**: 위험 대비 수익률 (높을수록 좋음)
- **변동성**: 가격 변동 폭 (리스크 지표)
- **최대 낙폭 (MDD)**: 최고점 대비 최대 하락률
- **배당 수익률**: 주가 대비 배당금 비율

## 🔮 확장 아이디어

- [ ] 포트폴리오 리밸런싱 제안
- [ ] 섹터별 자산 배분 분석
- [ ] 백테스팅 기능
- [ ] 알림 기능 (목표가 도달 시)
- [ ] 다중 포트폴리오 관리
- [ ] 엑셀 내보내기
- [ ] 모바일 반응형 개선

## 📝 라이선스

이 프로젝트는 개인 학습 및 포트폴리오 목적으로 제작되었습니다.

## 💡 참고사항

- yfinance 데이터는 15~20분 지연될 수 있습니다
- 한국 ETF는 `.KS` 또는 `.KQ` 접미사가 필요합니다
- 일부 ETF는 데이터가 제한적일 수 있습니다

---

**Made with ❤️ for ISA Investors**

