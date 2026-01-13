# DB 수정 완료 후 전환 가이드

## 📋 개요

현재는 **Redis 캐시**를 사용하여 더미 데이터로 API를 테스트하고 있습니다.
DB 수정이 완료되면 **실제 PostgreSQL DB**를 사용하도록 전환해야 합니다.

## 🔄 구조 변경 흐름

### 현재 구조 (DB 수정 중)
```
┌─────────────┐
│   사용자    │
│  (Client)   │
└──────┬──────┘
       │ HTTP 요청
       │ GET /api/v1/search/apartments?q=래미안
       ↓
┌─────────────────────────────────────┐
│         API (FastAPI)               │
│  app/api/v1/endpoints/search.py     │
└──────┬──────────────────────────────┘
       │
       │ RedisService 사용
       │ redis_svc.search_apartments_by_name()
       ↓
┌─────────────────────────────────────┐
│         Redis 캐시                  │
│  - 키: "apartments"                 │
│  - 값: JSON 문자열 (51개 더미 데이터)│
└──────┬──────────────────────────────┘
       │
       │ 필터링 및 정렬
       ↓
┌─────────────────────────────────────┐
│         API 응답                    │
│  {                                  │
│    "success": true,                 │
│    "data": { "results": [...] },   │
│    "meta": { "query": "...", ... } │
│  }                                  │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────┐
│   사용자    │
└─────────────┘
```

### 변경 후 구조 (DB 수정 완료)
```
┌─────────────┐
│   사용자    │
│  (Client)   │
└──────┬──────┘
       │ HTTP 요청
       │ GET /api/v1/search/apartments?q=래미안
       ↓
┌─────────────────────────────────────┐
│         API (FastAPI)               │
│  app/api/v1/endpoints/search.py     │
└──────┬──────────────────────────────┘
       │
       │ SQLAlchemy ORM 사용
       │ db.execute(select(Apartment)...)
       ↓
┌─────────────────────────────────────┐
│      PostgreSQL DB                    │
│  - 테이블: apartments                │
│  - 실제 데이터 (수천~수만 건)        │
│  - 인덱스: apt_name, sigungu_code    │
└──────┬──────────────────────────────┘
       │
       │ SQL 쿼리 결과
       ↓
┌─────────────────────────────────────┐
│         API 응답                    │
│  {                                  │
│    "success": true,                 │
│    "data": { "results": [...] },   │
│    "meta": { "query": "...", ... } │
│  }                                  │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────┐
│   사용자    │
└─────────────┘
```

## 📝 코드 변경 사항

### 1. search.py 엔드포인트 수정

#### 변경 전 (현재 - Redis 사용)
```python
# test-web/backend/app/api/v1/endpoints/search.py

from app.services.redis_service import get_redis_service

@router.get("/apartments")
async def search_apartments(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)  # 현재는 사용 안 함
):
    # Redis 캐시에서 데이터 가져오기
    apartments_data = []
    
    if USE_REDIS:
        try:
            redis_svc = get_redis_service()
            if redis_svc.connect():
                apartments_data = redis_svc.search_apartments_by_name(q, limit)
        except Exception as e:
            apartments_data = []
    
    # 응답 데이터 구성
    results = []
    for apt in apartments_data:
        result_item = {
            "apt_id": apt.get("apt_id"),
            "apt_name": apt.get("apt_name", ""),
            "address": apt.get("address", ""),
            "sigungu_name": apt.get("sigungu_name"),
            "dong_name": apt.get("dong_name"),
        }
        # ... location 정보 추가
        results.append(result_item)
    
    return {
        "success": True,
        "data": {"results": results},
        "meta": {"query": q, "count": len(results)}
    }
```

#### 변경 후 (DB 수정 완료 - 실제 DB 사용)
```python
# test-web/backend/app/api/v1/endpoints/search.py

from sqlalchemy import select
from app.models.apartment import Apartment

@router.get("/apartments")
async def search_apartments(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)  # 실제 DB 세션 사용
):
    # 실제 DB에서 아파트명 검색
    # ILIKE: 대소문자 구분 없이 검색 (PostgreSQL)
    result = await db.execute(
        select(Apartment)
        .where(Apartment.apt_name.ilike(f"%{q}%"))  # 부분 일치 검색
        .order_by(Apartment.apt_name)  # 이름순 정렬
        .limit(limit)  # 개수 제한
    )
    apartments = result.scalars().all()
    
    # 응답 데이터 구성 (형식은 동일)
    results = [
        {
            "apt_id": apt.apt_id,
            "apt_name": apt.apt_name,
            "address": apt.address,
            "sigungu_name": apt.sigungu_name,
            "dong_name": apt.dong_name,
            "location": {
                "lat": apt.latitude,
                "lng": apt.longitude
            } if apt.latitude and apt.longitude else None
        }
        for apt in apartments
    ]
    
    return {
        "success": True,
        "data": {"results": results},
        "meta": {"query": q, "count": len(results)}
    }
```

### 2. Import 문 변경

#### 변경 전
```python
# Redis 서비스 import
try:
    from app.services.redis_service import get_redis_service
    USE_REDIS = True
except ImportError:
    USE_REDIS = False
```

#### 변경 후
```python
# SQLAlchemy 및 모델 import
from sqlalchemy import select
from app.models.apartment import Apartment
# Redis 관련 import 제거
```

### 3. 의존성 주입 활용

#### 변경 전
```python
db: AsyncSession = Depends(get_db)  # 선언만 하고 사용 안 함
```

#### 변경 후
```python
db: AsyncSession = Depends(get_db)  # 실제로 사용
# db.execute(), db.commit() 등 사용
```

## 🔧 단계별 전환 절차

### Step 1: DB 연결 확인
```bash
# DB 연결 테스트
cd test-web/backend
python -c "from app.db.session import engine; print('DB 연결 성공')"
```

### Step 2: Apartment 모델 확인
```python
# test-web/backend/app/models/apartment.py 파일이 있는지 확인
# techeer-team-b-2026에서 복사하거나 동일한 구조인지 확인
```

### Step 3: 코드 수정
1. `search.py`에서 Redis 관련 코드 제거
2. SQLAlchemy 쿼리로 변경
3. Import 문 수정

### Step 4: 테스트
```bash
# 서버 실행
cd test-web/backend
python -m uvicorn app.main:app --reload

# API 테스트
curl "http://localhost:8000/api/v1/search/apartments?q=래미안&limit=10"
```

### Step 5: Redis 제거 (선택사항)
- 더 이상 필요 없으면 Redis 관련 파일 제거 가능
- 또는 테스트 환경으로 유지 가능

## 📊 주요 차이점 비교

| 항목 | 현재 (Redis) | 변경 후 (DB) |
|------|-------------|-------------|
| **데이터 소스** | Redis 캐시 (메모리) | PostgreSQL (디스크) |
| **데이터 개수** | 51개 (고정) | 수천~수만 건 (동적) |
| **검색 방식** | Python 리스트 필터링 | SQL 쿼리 (ILIKE) |
| **성능** | 매우 빠름 (메모리) | 빠름 (인덱스 활용) |
| **데이터 동기화** | 수동 로드 필요 | 자동 (DB에 저장) |
| **영구 저장** | ❌ (재시작 시 사라짐) | ✅ (영구 저장) |
| **확장성** | 제한적 (메모리 제한) | 높음 (디스크 저장) |

## ⚠️ 주의사항

### 1. 응답 형식 유지
- API 응답 형식은 **동일하게 유지**해야 합니다
- 클라이언트 코드 변경 불필요

### 2. 에러 처리
```python
# DB 연결 실패 시 에러 처리 추가
try:
    result = await db.execute(...)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"DB 오류: {str(e)}")
```

### 3. 성능 최적화
- DB 인덱스 확인: `apt_name`에 인덱스가 있는지 확인
- 필요시 Redis 캐시 레이어 추가 고려 (2차 캐싱)

### 4. 테스트
- 기존 테스트 케이스가 있다면 모두 통과하는지 확인
- 실제 데이터로 검색 결과 검증

## 🔄 점진적 전환 방법 (선택사항)

### Option 1: Feature Flag 사용
```python
USE_REAL_DB = os.getenv("USE_REAL_DB", "false").lower() == "true"

if USE_REAL_DB:
    # 실제 DB 사용
    result = await db.execute(select(Apartment)...)
else:
    # Redis 사용 (기존 코드)
    apartments_data = redis_svc.search_apartments_by_name(q, limit)
```

### Option 2: Fallback 패턴
```python
try:
    # 먼저 실제 DB 시도
    result = await db.execute(select(Apartment)...)
    apartments = result.scalars().all()
except Exception:
    # DB 실패 시 Redis로 fallback
    apartments_data = redis_svc.search_apartments_by_name(q, limit)
```

## 📚 관련 파일

### 변경 대상 파일
- `test-web/backend/app/api/v1/endpoints/search.py` ⭐ **주요 변경**
- `test-web/backend/app/api/v1/router.py` (변경 불필요)

### 참고 파일
- `techeer-team-b-2026/backend/app/api/v1/endpoints/search_apart.py` (실제 DB 사용 예시)
- `techeer-team-b-2026/backend/app/models/apartment.py` (DB 모델)

### 유지 가능 파일 (테스트용)
- `test-web/api-test/mock-data/apartments.json` (테스트 데이터)
- `test-web/backend/app/services/redis_service.py` (테스트 환경용)

## ✅ 체크리스트

전환 전 확인 사항:
- [ ] DB 연결 설정 완료 (`app/db/session.py`)
- [ ] Apartment 모델 존재 확인
- [ ] DB에 실제 데이터 존재 확인
- [ ] 인덱스 생성 확인 (`apt_name` 인덱스)

전환 후 확인 사항:
- [ ] API 응답 형식 동일한지 확인
- [ ] 검색 결과 정확성 확인
- [ ] 성능 테스트 (응답 시간)
- [ ] 에러 처리 동작 확인

## 🎯 요약

1. **코드 변경**: Redis → SQLAlchemy 쿼리로 변경
2. **응답 형식**: 동일하게 유지 (클라이언트 변경 불필요)
3. **데이터 소스**: Redis 캐시 → PostgreSQL DB
4. **성능**: 인덱스 활용으로 빠른 검색 가능
5. **확장성**: 수천~수만 건의 데이터 처리 가능

**핵심**: 응답 형식은 그대로 유지하고, 데이터 소스만 Redis에서 DB로 변경하면 됩니다!
