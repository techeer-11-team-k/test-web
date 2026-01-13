# Redis 캐시 아키텍처 설명

## 📋 개요

현재 DB가 수정 중이므로, 실제 DB 대신 **Redis 캐시**를 활용하여 API 테스트를 진행합니다.
실제 DB 구조와 동일한 형식의 더미 데이터를 Redis에 저장하여, API가 정상적으로 동작하는지 테스트할 수 있습니다.

## 🏗️ 아키텍처 흐름

### 실제 운영 환경 (DB 수정 완료 후)
```
사용자 요청
    ↓
API (FastAPI)
    ↓
DB (PostgreSQL) ← 실제 데이터 저장
    ↓
API 응답
    ↓
사용자
```

### 현재 테스트 환경 (DB 수정 중)
```
사용자 요청
    ↓
API (FastAPI)
    ↓
Redis 캐시 ← 더미 데이터 (실제 DB 구조와 동일)
    ↓
API 응답
    ↓
사용자
```

## 🔄 데이터 흐름 상세

### 1. 더미 데이터 로드
```
apartments.json (51개 한글 아파트 데이터)
    ↓
load_mock_data.py 스크립트 실행
    ↓
Redis에 JSON 형식으로 저장
```

### 2. API 요청 처리
```
GET /api/v1/search/apartments?q=래미안&limit=10
    ↓
search.py 엔드포인트
    ↓
RedisService.search_apartments_by_name()
    ↓
Redis에서 데이터 조회 및 필터링
    ↓
응답 반환 (실제 DB 응답 형식과 동일)
```

## 📊 데이터 구조

### 실제 DB 구조 (apartments 테이블)
```sql
CREATE TABLE apartments (
    apt_id SERIAL PRIMARY KEY,
    apt_name VARCHAR(200) NOT NULL,
    address VARCHAR(500),
    sigungu_code VARCHAR(10),
    sigungu_name VARCHAR(50),
    dong_name VARCHAR(50),
    latitude FLOAT,
    longitude FLOAT,
    total_units INTEGER,
    build_year INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Redis 저장 구조
```json
{
  "apartments": [
    {
      "apt_id": 1,
      "apt_name": "래미안 강남파크",
      "address": "서울특별시 강남구 역삼동 123-45",
      "sigungu_code": "11680",
      "sigungu_name": "강남구",
      "dong_name": "역삼동",
      "latitude": 37.5012,
      "longitude": 127.0375,
      "total_units": 850,
      "build_year": 2018,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    ...
  ]
}
```

Redis 키: `apartments` (String 타입, JSON 문자열로 저장)

## 🔧 주요 컴포넌트

### 1. 더미 데이터 파일
- **위치**: `test-web/api-test/mock-data/apartments.json`
- **내용**: 51개의 한글 아파트 데이터
- **형식**: 실제 DB 구조와 동일한 필드명 사용

### 2. 데이터 로더 스크립트
- **위치**: `test-web/api-test/scripts/load_mock_data.py`
- **기능**: JSON 파일을 읽어서 Redis에 저장
- **실행**: `python api-test/scripts/load_mock_data.py`

### 3. Redis 서비스
- **위치**: `test-web/backend/app/services/redis_service.py`
- **주요 메서드**:
  - `get_all_apartments()`: 모든 아파트 조회
  - `get_apartment(apt_id)`: 특정 아파트 조회
  - `search_apartments_by_name(query, limit)`: 아파트명 검색

### 4. 검색 API 엔드포인트
- **위치**: `test-web/backend/app/api/v1/endpoints/search.py`
- **엔드포인트**: `GET /api/v1/search/apartments?q={검색어}&limit={개수}`
- **동작**: Redis에서 데이터를 조회하여 실제 DB 응답 형식으로 반환

## 🚀 사용 방법

### 1. Redis 실행
```bash
cd test-web
docker-compose up -d redis
```

### 2. 더미 데이터 로드
```bash
cd test-web
python api-test/scripts/load_mock_data.py
```

### 3. 백엔드 서버 실행
```bash
cd test-web/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. API 테스트
```bash
# Swagger UI
http://localhost:8000/docs

# 직접 호출
curl "http://localhost:8000/api/v1/search/apartments?q=래미안&limit=10"
```

## 📝 주요 특징

### 1. 실제 DB 구조와 동일
- 필드명: `apt_id`, `apt_name`, `sigungu_name`, `dong_name` 등
- 데이터 타입: int, string, float 등 실제 DB와 동일
- 응답 형식: `search_apart.py`와 동일한 구조

### 2. 한글 데이터
- 51개의 실제 아파트명과 유사한 한글 데이터
- 서울, 경기, 부산, 대구, 광주 등 다양한 지역 포함
- 실제 주소 형식 사용

### 3. 검색 기능
- 아파트명 부분 일치 검색 (대소문자 구분 없음)
- 이름순 정렬
- limit으로 결과 개수 제한

## ⚠️ 주의사항

1. **Redis 연결 실패 시**: 빈 결과(`[]`)를 반환합니다.
2. **데이터 동기화**: Redis 데이터는 실제 DB와 동기화되지 않습니다.
3. **캐시 만료**: Redis 데이터는 수동으로 삭제하지 않는 한 유지됩니다.
4. **DB 수정 완료 후**: 실제 DB로 전환 시 코드 수정이 필요합니다.

## 🔄 DB 수정 완료 후 전환 방법

1. `search.py`에서 Redis 대신 실제 DB 쿼리 사용
2. `get_db` 의존성으로 DB 세션 사용
3. SQLAlchemy 쿼리로 데이터 조회

```python
# 변경 전 (Redis 사용)
apartments_data = redis_svc.search_apartments_by_name(q, limit)

# 변경 후 (실제 DB 사용)
result = await db.execute(
    select(Apartment)
    .where(Apartment.apt_name.ilike(f"%{q}%"))
    .order_by(Apartment.apt_name)
    .limit(limit)
)
apartments = result.scalars().all()
```

## 📚 관련 파일

- `test-web/api-test/mock-data/apartments.json`: 더미 데이터
- `test-web/api-test/scripts/load_mock_data.py`: 데이터 로더
- `test-web/backend/app/services/redis_service.py`: Redis 서비스
- `test-web/backend/app/api/v1/endpoints/search.py`: 검색 API
- `techeer-team-b-2026/backend/app/models/apartment.py`: 실제 DB 모델 (참고용)
