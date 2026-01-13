# 📊 ERD (Entity Relationship Diagram) 구조 설명

## 🎯 개요

부동산 분석 플랫폼의 데이터베이스 ERD 구조를 설명합니다.

---

## 📋 주요 테이블 목록

| 테이블명 | 설명 | 주요 용도 |
|---------|------|----------|
| `ACCOUNTS` | 사용자 계정 | Clerk 인증 연동, 사용자 정보 관리 |
| `APARTMENTS` | 아파트 정보 | 아파트 기본 정보 저장 |
| `STATES` | 시군구 정보 | 지역 정보 (시/군/구) |
| `TRANSACTIONS` | 실거래 내역 | 매매/전세/월세 거래 정보 |
| `FAVORITE_APARTMENTS` | 즐겨찾기 아파트 | 사용자가 즐겨찾기한 아파트 |
| `FAVORITE_LOCATIONS` | 즐겨찾기 지역 | 사용자가 즐겨찾기한 지역 |
| `MY_PROPERTIES` | 내 집 정보 | 사용자가 소유한 부동산 정보 |
| `HOUSE_SCORE` | 주택가격지수 | KB부동산 주택가격지수 데이터 |

---

## 🏠 APARTMENTS 테이블 상세 구조

### 현재 API 응답 데이터
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

### 실제 데이터베이스 구조

```sql
CREATE TABLE `APARTMENTS` (
  -- 기본키
  `apt_id` INT NOT NULL PRIMARY KEY COMMENT 'PK',
  
  -- 외래키 (지역 정보)
  `region_id` INT NOT NULL COMMENT 'FK → STATES.region_id',
  
  -- 기본 정보
  `apt_name` VARCHAR(100) NOT NULL COMMENT '아파트 단지명',
  `kapt_code` VARCHAR(20) NOT NULL COMMENT '국토부 단지코드',
  
  -- 주소 정보
  `road_address` VARCHAR(200) NOT NULL COMMENT '도로명주소 (카카오 API)',
  `jibun_address` VARCHAR(200) NOT NULL COMMENT '지번주소 (카카오 API)',
  `zip_code` CHAR(5) NULL COMMENT '우편번호',
  
  -- 단지 정보
  `total_household_cnt` INT NOT NULL COMMENT '총 세대수',
  `total_building_cnt` INT NULL COMMENT '총 동수',
  `highest_floor` INT NULL COMMENT '최고층',
  `use_approval_date` DATE NULL COMMENT '준공일',
  `total_parking_cnt` INT NULL COMMENT '주차대수',
  
  -- 건설 정보
  `builder_name` VARCHAR(100) NULL COMMENT '건설사',
  `developer_name` VARCHAR(100) NULL COMMENT '시공사',
  
  -- 관리 정보
  `manage_type` VARCHAR(20) NULL COMMENT '관리유형 (자치관리/위탁관리)',
  `hallway_type` VARCHAR(20) NULL COMMENT '복도유형 (계단식/복도식/혼합식)',
  `code_heat_nm` VARCHAR(20) NULL COMMENT '난방방식 (지역난방/개별난방)',
  `code_sale_nm` VARCHAR(20) NULL COMMENT '분양/임대 구분',
  
  -- 교통 정보
  `subway_line` VARCHAR(100) NULL COMMENT '지하철 노선',
  `subway_station` VARCHAR(100) NULL COMMENT '지하철 역명',
  `subway_time` VARCHAR(100) NULL COMMENT '지하철 도보시간',
  
  -- 교육 정보
  `educationFacility` VARCHAR(100) NULL COMMENT '교육시설 정보',
  
  -- ⭐ 위치 정보 (PostGIS)
  `geometry` GEOMETRY(POINT, 4326) NOT NULL COMMENT '위치 좌표 (WGS84)',
  
  -- 메타 정보
  `created_at` TIMESTAMP NOT NULL,
  `updated_at` TIMESTAMP NOT NULL,
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '소프트 삭제'
);
```

### 현재 API vs 실제 DB 비교

| 항목 | 현재 API 응답 | 실제 DB 컬럼 | 비고 |
|------|--------------|-------------|------|
| 아파트 ID | `apt_id` | `apt_id` | ✅ 동일 |
| 아파트명 | `apt_name` | `apt_name` | ✅ 동일 |
| 주소 | `address` | `road_address`, `jibun_address` | DB는 분리됨 |
| 시군구명 | `sigungu_name` | `STATES.region_name` (JOIN) | FK 관계 |
| 동명 | `dong_name` | `STATES` 테이블에서 조회 | FK 관계 |
| 위치 | `location.lat/lng` | `geometry` (PostGIS Point) | PostGIS 사용 |

---

## 🔗 테이블 간 관계 (Relationships)

### 1. APARTMENTS ↔ STATES (N:1)
```
APARTMENTS (다수) ──[region_id]──> STATES (1개)
```
- 하나의 시군구(STATES)에 여러 아파트(APARTMENTS)가 속함
- `APARTMENTS.region_id` → `STATES.region_id` (FK)

### 2. APARTMENTS ↔ TRANSACTIONS (1:N)
```
APARTMENTS (1개) ──[apt_id]──> TRANSACTIONS (다수)
```
- 하나의 아파트에 여러 거래 내역이 존재
- `TRANSACTIONS.apt_id` → `APARTMENTS.apt_id` (FK)

### 3. ACCOUNTS ↔ FAVORITE_APARTMENTS (1:N)
```
ACCOUNTS (1개) ──[account_id]──> FAVORITE_APARTMENTS (다수)
```
- 한 사용자가 여러 아파트를 즐겨찾기 가능
- `FAVORITE_APARTMENTS.account_id` → `ACCOUNTS.account_id` (FK)

### 4. ACCOUNTS ↔ MY_PROPERTIES (1:N)
```
ACCOUNTS (1개) ──[account_id]──> MY_PROPERTIES (다수)
```
- 한 사용자가 여러 부동산을 소유 가능
- `MY_PROPERTIES.account_id` → `ACCOUNTS.account_id` (FK)

### 5. APARTMENTS ↔ FAVORITE_APARTMENTS (1:N)
```
APARTMENTS (1개) ──[apt_id]──> FAVORITE_APARTMENTS (다수)
```
- 하나의 아파트가 여러 사용자에게 즐겨찾기될 수 있음
- `FAVORITE_APARTMENTS.apt_id` → `APARTMENTS.apt_id` (FK)

---

## 📐 ERD 다이어그램 (텍스트 버전)

```
┌─────────────────┐
│   ACCOUNTS      │
├─────────────────┤
│ account_id (PK) │
│ clerk_user_id   │
│ email           │
│ nickname        │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴──────────────────────────────┐
    │                                   │
    ▼                                   ▼
┌──────────────────┐        ┌──────────────────┐
│FAVORITE_APARTMENTS│        │  MY_PROPERTIES   │
├──────────────────┤        ├──────────────────┤
│ favorite_id (PK) │        │ property_id (PK) │
│ account_id (FK)  │        │ account_id (FK)  │
│ apt_id (FK)      │        │ apt_id (FK)      │
└────────┬─────────┘        └────────┬─────────┘
         │                           │
         │ N:1                       │ N:1
         │                           │
         └───────────┬───────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │   APARTMENTS    │
            ├─────────────────┤
            │ apt_id (PK)     │
            │ region_id (FK)  │
            │ apt_name        │
            │ road_address    │
            │ geometry        │
            └────────┬────────┘
                     │
                     │ N:1
                     │
                     ▼
            ┌─────────────────┐
            │     STATES      │
            ├─────────────────┤
            │ region_id (PK)  │
            │ region_name     │
            │ region_code     │
            └─────────────────┘
                     │
                     │ 1:N
                     │
                     ▼
            ┌─────────────────┐
            │  TRANSACTIONS   │
            ├─────────────────┤
            │ trans_id (PK)   │
            │ apt_id (FK)     │
            │ trans_type      │
            │ trans_price     │
            └─────────────────┘
```

---

## 🔍 주요 특징

### 1. PostGIS 사용
- `APARTMENTS.geometry`: PostGIS Point 타입 사용
- SRID 4326 (WGS84 좌표계) = GPS 좌표
- 지리적 검색 및 거리 계산 가능

### 2. 소프트 삭제 (Soft Delete)
- 모든 테이블에 `is_deleted` 컬럼 존재
- 실제 삭제 대신 플래그로 관리
- 데이터 복구 가능

### 3. 타임스탬프 자동 관리
- `created_at`: 레코드 생성 시 자동 설정
- `updated_at`: 레코드 수정 시 자동 업데이트

### 4. 인덱스 최적화
- `apt_name`: 검색 성능을 위한 인덱스
- `sigungu_code`: 지역 검색을 위한 인덱스
- `clerk_user_id`, `email`: 유니크 인덱스

---

## 📝 현재 API와 실제 DB의 차이점

### 현재 API 응답 (간소화 버전)
```json
{
  "apt_id": 1,
  "apt_name": "래미안 강남파크",
  "address": "서울특별시 강남구 역삼동 123-45",
  "sigungu_name": "강남구",
  "dong_name": "역삼동",
  "location": {"lat": 37.5012, "lng": 127.0375}
}
```

### 실제 DB 조회 시 필요한 JOIN
```sql
SELECT 
  a.apt_id,
  a.apt_name,
  a.road_address AS address,
  s.region_name AS sigungu_name,
  s.dong_name,
  ST_X(a.geometry) AS lat,
  ST_Y(a.geometry) AS lng
FROM APARTMENTS a
JOIN STATES s ON a.region_id = s.region_id
WHERE a.is_deleted = 0;
```

### 차이점 요약
1. **주소**: API는 단일 `address`, DB는 `road_address` + `jibun_address` 분리
2. **위치**: API는 `lat/lng` 분리, DB는 PostGIS `geometry` Point
3. **지역 정보**: API는 직접 포함, DB는 `STATES` 테이블과 JOIN 필요
4. **추가 정보**: DB에는 더 많은 컬럼 존재 (세대수, 준공일, 건설사 등)

---

## 🚀 향후 개선 사항

1. **API 응답 확장**: DB의 추가 컬럼들을 API에 포함
2. **JOIN 최적화**: `STATES` 테이블과 JOIN하여 지역 정보 제공
3. **PostGIS 활용**: 거리 기반 검색, 반경 검색 기능 추가
4. **인덱스 최적화**: 검색 성능 향상을 위한 인덱스 추가

---

## 📚 참고 자료

- [PostGIS 공식 문서](https://postgis.net/)
- [SQLAlchemy ORM 문서](https://docs.sqlalchemy.org/)
- [ERD 설계 가이드](https://www.lucidchart.com/pages/er-diagrams)
