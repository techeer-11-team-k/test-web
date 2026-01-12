# 🚀 빠른 시작 가이드

이 가이드는 프로젝트를 빠르게 실행하는 방법을 안내합니다.

## ⚡ 5분 안에 시작하기

### 1. 환경 변수 설정

```bash
# 루트 디렉토리에서
cp env.txt .env

# .env 파일을 열어서 Clerk 키를 설정하세요
# CLERK_PUBLISHABLE_KEY=pk_test_...
# CLERK_SECRET_KEY=sk_test_...
```

### 2. 데이터베이스 실행

```bash
# Docker로 데이터베이스와 Redis 실행
docker-compose up -d db redis

# 데이터베이스 초기화 (테이블 생성)
docker exec -i realestate-db psql -U postgres -d realestate < backend/scripts/init_db.sql
```

### 3. 백엔드 실행

```bash
# Docker로 백엔드 실행
docker-compose up -d backend

# 또는 로컬에서 실행
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

백엔드 API: http://localhost:8000
API 문서: http://localhost:8000/docs

### 4. 프론트엔드 실행

```bash
cd frontend

# 의존성 설치
npm install

# .env 파일 생성
echo "VITE_API_BASE_URL=http://localhost:8000/api/v1" > .env
echo "VITE_CLERK_PUBLISHABLE_KEY=pk_test_..." >> .env

# 개발 서버 실행
npm run dev
```

프론트엔드: http://localhost:3000

---

## ✅ 확인 사항

### 데이터베이스 연결 확인

```bash
# Docker 컨테이너 상태 확인
docker-compose ps

# 데이터베이스 테이블 확인
docker exec -it realestate-db psql -U postgres -d realestate -c "\dt"
```

`accounts` 테이블이 보이면 성공!

### 백엔드 API 확인

브라우저에서 http://localhost:8000/health 접속
응답: `{"status":"healthy","service":"부동산 데이터 분석 서비스"}`

### 프론트엔드 확인

브라우저에서 http://localhost:3000 접속
로그인 버튼이 보이면 성공!

---

## 🔧 문제 해결

### 포트가 이미 사용 중입니다

```bash
# 포트 확인
lsof -i :8000  # 백엔드
lsof -i :3000  # 프론트엔드
lsof -i :5432  # 데이터베이스

# Docker 컨테이너 중지
docker-compose down
```

### 데이터베이스 연결 실패

```bash
# Docker 컨테이너 재시작
docker-compose restart db

# 로그 확인
docker-compose logs db
```

### Clerk 인증 오류

- `.env` 파일에 `VITE_CLERK_PUBLISHABLE_KEY`가 올바르게 설정되었는지 확인
- Clerk Dashboard에서 애플리케이션이 활성화되어 있는지 확인

---

## 📚 더 자세한 정보

- [프로젝트 README](./readme.md)
- [전체 설정 가이드](./README_SETUP.md)
- [API 문서](./docs/api_docs.md)
- [API 개발 체크리스트](./docs/api_check.md)
- [백엔드 문서](./backend/docs/README.md)
