# 📊 API 응답 데이터와 ERD 매핑 관계

## 🎯 개요

현재 API 응답 데이터가 데이터베이스 ERD 구조와 어떻게 연결되는지 설명합니다.

---

## 📋 현재 API 응답 데이터

```json
{
  "apt_id": 1,
  "apt_name": "래미안 강남파크",
  "address": "서울특별시 강남구 역삼동 123-45",
  "sigungu_name": "강남구",
  "dong_name": "역삼동",
  "location": {
    "lat": 37.5012,
    "lng": 127.0375
  }
}
```

---

## 🗄️ ERD 테이블 구조와 매핑

### 1. APARTMENTS 테이블 (메인 테이블)

현재 API 응답의 모든 데이터는 **`APARTMENTS` 테이블**에서 직접 가져옵니다.

#### 직접 매핑되는 필드

| API 응답 필드 | DB 컬럼명 | 타입 | 설명 |
|--------------|-----------|------|------|
| `apt_id` | `apt_id` | `INT` (PK) | 아파트 고유 ID |
| `apt_name` | `apt_name` | `VARCHAR(200)` | 아파트명 |
| `address` | `address` | `VARCHAR(500)` | 전체 주소 |
| `sigungu_name` | `sigungu_name` | `VARCHAR(50)` | 시군구명 |
| `dong_name` | `dong_name` | `VARCHAR(50)` | 동명 |
| `location.lat` | `latitude` | `FLOAT` | 위도 |
| `location.lng` | `longitude` | `FLOAT` | 경도 |

---

## 🔄 데이터 변환 과정

### 실제 DB 쿼리 (search_apart.py 기준)

```python
# 1. DB에서 아파트 검색
result = await db.execute(
    select(Apartment)
    .where(Apartment.apt_name.ilike(f"%{q}%"))
    .order_by(Apartment.apt_name)
    .limit(limit)
)
apartments = result.scalars().all()

# 2. 응답 데이터로 변환
results = [
    {
        "apt_id": apt.apt_id,              # ← APARTMENTS.apt_id
        "apt_name": apt.apt_name,          # ← APARTMENTS.apt_name
        "address": apt.address,            # ← APARTMENTS.address
        "sigungu_name": apt.sigungu_name,  # ← APARTMENTS.sigungu_name
        "dong_name": apt.dong_name,        # ← APARTMENTS.dong_name
        "location": {
            "lat": apt.latitude,           # ← APARTMENTS.latitude
            "lng": apt.longitude           # ← APARTMENTS.longitude
        } if apt.latitude and apt.longitude else None
    }
    for apt in apartments
]
```

### SQL 쿼리로 표현하면

```sql
SELECT 
    apt_id,           -- → API: apt_id
    apt_name,         -- → API: apt_name
    address,          -- → API: address
    sigungu_name,     -- → API: sigungu_name
    dong_name,        -- → API: dong_name
    latitude,         -- → API: location.lat
    longitude         -- → API: location.lng
FROM apartments
WHERE apt_name ILIKE '%래미안%'
ORDER BY apt_name
LIMIT 10;
```

---

## 📐 ERD 관계도에서의 위치

```
┌─────────────────────────────────┐
│      APARTMENTS 테이블           │
├─────────────────────────────────┤
│ apt_id (PK) ────────────────┐   │
│ apt_name                     │   │
│ address                      │   │
│ sigungu_name                 │   │
│ dong_name                    │   │
│ latitude                      │   │
│ longitude                     │   │
│ ────────────────────────────────│
│ region_id (FK) ──────────────┼──→│ STATES 테이블
│ total_units                   │   │ (현재 API에서는 미사용)
│ build_year                    │   │
│ created_at                    │   │
│ updated_at                    │   │
└─────────────────────────────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────────────────────┐
│    TRANSACTIONS 테이블           │
│ (현재 API에서는 미사용)          │
└─────────────────────────────────┘
```

---

## 🔍 필드별 상세 설명

### 1. `apt_id` (기본키)
- **ERD 위치**: `APARTMENTS.apt_id` (Primary Key)
- **특징**: 
  - 자동 증가 (AUTO_INCREMENT)
  - 다른 테이블에서 외래키로 참조 가능
  - 예: `TRANSACTIONS.apt_id`, `FAVORITE_APARTMENTS.apt_id`

### 2. `apt_name` (아파트명)
- **ERD 위치**: `APARTMENTS.apt_name`
- **특징**:
  - 인덱스가 설정되어 있어 검색 성능 최적화
  - `ILIKE` 연산자로 부분 일치 검색 가능

### 3. `address` (주소)
- **ERD 위치**: `APARTMENTS.address`
- **특징**:
  - 현재는 단일 주소 필드
  - 실제 프로덕션에서는 `road_address`(도로명)와 `jibun_address`(지번)로 분리될 수 있음

### 4. `sigungu_name` (시군구명)
- **ERD 위치**: `APARTMENTS.sigungu_name`
- **특징**:
  - 현재는 `APARTMENTS` 테이블에 직접 저장
  - 정규화된 구조에서는 `STATES` 테이블과 JOIN하여 가져올 수 있음
  - 예: `SELECT s.region_name FROM apartments a JOIN states s ON a.region_id = s.region_id`

### 5. `dong_name` (동명)
- **ERD 위치**: `APARTMENTS.dong_name`
- **특징**:
  - 현재는 `APARTMENTS` 테이블에 직접 저장
  - 정규화된 구조에서는 `STATES` 테이블에서 가져올 수 있음

### 6. `location.lat` / `location.lng` (위치)
- **ERD 위치**: `APARTMENTS.latitude`, `APARTMENTS.longitude`
- **특징**:
  - API에서는 중첩 객체(`location`)로 제공
  - DB에서는 두 개의 분리된 컬럼으로 저장
  - PostGIS를 사용하는 경우 `geometry` Point 타입으로 저장 가능

---

## 🔗 다른 테이블과의 관계 (현재 미사용)

### 1. STATES 테이블 (지역 정보)
- **관계**: `APARTMENTS.region_id` → `STATES.region_id` (FK)
- **현재 상태**: API 응답에 직접 포함되지 않음
- **향후 활용**: 지역별 통계, 지역 검색 기능에 사용 가능

### 2. TRANSACTIONS 테이블 (거래 내역)
- **관계**: `TRANSACTIONS.apt_id` → `APARTMENTS.apt_id` (FK)
- **현재 상태**: 검색 API에서는 미사용
- **향후 활용**: 아파트 상세 정보 조회 시 거래 내역 포함 가능

### 3. FAVORITE_APARTMENTS 테이블 (즐겨찾기)
- **관계**: `FAVORITE_APARTMENTS.apt_id` → `APARTMENTS.apt_id` (FK)
- **현재 상태**: 검색 API에서는 미사용
- **향후 활용**: 사용자별 즐겨찾기 여부 표시 가능

---

## 📊 데이터 흐름도

```
┌─────────────────────────────────────────────────────────┐
│                    사용자 요청                           │
│  GET /api/v1/search/apartments?q=래미안                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI 엔드포인트                          │
│         search_apartments() 함수                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              SQLAlchemy ORM 쿼리                        │
│  select(Apartment).where(apt_name.ilike('%래미안%'))     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL 데이터베이스                     │
│              APARTMENTS 테이블                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │ apt_id │ apt_name │ address │ sigungu_name │ ... │   │
│  │   1    │ 래미안... │ 서울... │   강남구    │ ... │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Python 객체 변환                            │
│  Apartment(apt_id=1, apt_name="래미안...", ...)          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              응답 데이터 변환                            │
│  {                                                       │
│    "apt_id": 1,                                         │
│    "apt_name": "래미안 강남파크",                        │
│    "location": {"lat": 37.5012, "lng": 127.0375}        │
│  }                                                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              JSON 응답 반환                              │
│  {                                                       │
│    "success": true,                                     │
│    "data": {"results": [...]},                          │
│    "meta": {"query": "래미안", "count": 5}              │
│  }                                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 핵심 요약

1. **단일 테이블 조회**: 현재 API는 `APARTMENTS` 테이블만 조회
2. **직접 매핑**: 모든 필드가 `APARTMENTS` 테이블의 컬럼과 1:1 매핑
3. **JOIN 없음**: 현재는 다른 테이블과 JOIN하지 않음
4. **데이터 변환**: `latitude`/`longitude` → `location.lat`/`location.lng`로 구조 변환
5. **확장 가능**: 향후 `STATES`, `TRANSACTIONS` 테이블과 JOIN하여 더 많은 정보 제공 가능

---

## 💡 향후 개선 방향

### 1. 지역 정보 정규화
```sql
-- 현재
SELECT sigungu_name, dong_name FROM apartments WHERE apt_id = 1;

-- 향후 (정규화)
SELECT s.region_name, s.dong_name 
FROM apartments a
JOIN states s ON a.region_id = s.region_id
WHERE a.apt_id = 1;
```

### 2. 거래 내역 포함
```json
{
  "apt_id": 1,
  "apt_name": "래미안 강남파크",
  "recent_transactions": [
    {
      "trans_id": 100,
      "trans_price": 120000,
      "deal_date": "2024-01-15"
    }
  ]
}
```

### 3. PostGIS 활용
```sql
-- 현재
SELECT latitude, longitude FROM apartments WHERE apt_id = 1;

-- 향후 (PostGIS)
SELECT ST_X(geometry) AS lat, ST_Y(geometry) AS lng 
FROM apartments 
WHERE apt_id = 1;
```

---

## 📚 참고

- **현재 모델**: `techeer-team-b-2026/backend/app/models/apartment.py`
- **API 엔드포인트**: `techeer-team-b-2026/backend/app/api/v1/endpoints/search_apart.py`
- **ERD 구조**: `test-web/docs/erd-structure.md`
