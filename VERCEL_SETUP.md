# Vercel 배포 가이드 (PostgreSQL)

## 🚀 Vercel에 배포하기

### 1. Vercel 프로젝트 생성
1. https://vercel.com 로그인
2. **Add New** → **Project**
3. GitHub 레포지토리 선택: `una0801/ETFolio`

### 2. 프로젝트 설정

#### Framework Preset
- **FastAPI** 선택

#### Root Directory
- `./` (기본값)

#### Build Settings
- **Build Command**: 비워두기 또는 `None`
- **Output Directory**: 비워두기 또는 `N/A`
- **Install Command**: `pip install -r requirements.txt`

### 3. PostgreSQL 데이터베이스 생성 ⭐

배포하기 **전에** 데이터베이스를 먼저 만드세요!

1. Vercel 대시보드에서 **Storage** 탭
2. **Create Database** 클릭
3. **Postgres** 선택
4. 데이터베이스 이름: `etfolio-db` (또는 원하는 이름)
5. **Create** 클릭

### 4. 환경 변수 자동 연결

PostgreSQL을 생성하면 Vercel이 자동으로 다음 환경 변수를 설정합니다:
- `POSTGRES_URL`
- `POSTGRES_PRISMA_URL`
- `POSTGRES_URL_NON_POOLING`
- 기타 PostgreSQL 관련 변수들

우리 코드는 **`POSTGRES_URL`**을 자동으로 감지하고 사용합니다!

### 5. 추가 환경 변수 (선택사항)

필요하다면 수동으로 추가:
- `DEBUG`: `False`
- `APP_NAME`: `ETFolio`

### 6. 배포
**Deploy** 버튼 클릭! 🚀

---

## ✅ 배포 후 확인

배포가 완료되면:
1. **메인 페이지**: `https://your-app.vercel.app/`
2. **API 문서**: `https://your-app.vercel.app/docs`
3. **헬스 체크**: `https://your-app.vercel.app/health`

---

## 🔄 데이터베이스 마이그레이션

처음 배포 시 테이블이 자동 생성됩니다 (`init_db()` 함수).

만약 수동으로 테이블을 생성해야 한다면:
1. Vercel 대시보드 → **Storage** → PostgreSQL 클릭
2. **Data** 탭에서 SQL 쿼리 실행 가능

---

## 🏠 로컬 개발 환경

로컬에서는 여전히 SQLite를 사용합니다:
```bash
# .env 파일
DATABASE_URL=sqlite:///./etfolio.db
```

`POSTGRES_URL`이 없으면 자동으로 SQLite 사용!

---

## 🔧 PostgreSQL 직접 연결 (로컬에서 테스트)

로컬에서도 PostgreSQL을 사용하려면:
```bash
# .env
POSTGRES_URL=postgresql://user:password@localhost:5432/etfolio
```

---

## ⚡ 자동 전환 로직

우리 코드는 똑똑합니다:
- **Vercel (프로덕션)**: `POSTGRES_URL` 감지 → PostgreSQL 사용
- **로컬 개발**: `POSTGRES_URL` 없음 → SQLite 사용

별도 설정 없이 자동으로 환경에 맞게 작동합니다! 🎉

---

## 📝 요약

### Vercel 배포 순서
1. ✅ Storage에서 PostgreSQL 생성
2. ✅ GitHub 레포 연결
3. ✅ Framework: FastAPI
4. ✅ Install Command: `pip install -r requirements.txt`
5. ✅ Build/Output: 비우기
6. ✅ Deploy 클릭

끝! PostgreSQL은 Vercel이 자동으로 연결해줍니다. 🚀

