# 🏠 아파트 검색 POC - React Native

`techeer-team-b-2026`의 `search_apart` API를 테스트하는 React Native 앱입니다.

## 📋 기능

- 아파트명 검색 (2글자 이상)
- 자동완성 검색 (디바운싱 500ms)
- 결과 개수 제한 설정 (10, 20, 30, 50개)
- 아파트 정보 표시 (이름, 주소, 위치)

## 🚀 실행 방법

### 1. 의존성 설치

```bash
cd react-native-app
npm install
```

### 2. API 서버 주소 설정

`App.tsx` 파일에서 API 주소를 수정하세요:

```typescript
// 로컬 개발 시
const API_BASE_URL = 'http://localhost:8000/api/v1/search';

// 실제 디바이스/에뮬레이터에서 테스트 시
// Android 에뮬레이터: http://10.0.2.2:8000/api/v1/search
// iOS 시뮬레이터: http://localhost:8000/api/v1/search
// 실제 디바이스: http://[컴퓨터IP]:8000/api/v1/search
```

### 3. 앱 실행

```bash
# Expo 시작
npm start

# 또는
npx expo start

# 특정 플랫폼 실행
npm run android  # Android
npm run ios      # iOS
npm run web      # Web
```

## 📱 테스트 방법

1. 앱 실행 후 검색창에 아파트명 입력 (최소 2글자)
2. 자동으로 검색 결과가 표시됩니다
3. 결과 개수 버튼으로 제한 변경 가능

## 🔧 API 엔드포인트

- **URL**: `GET /api/v1/search/apartments`
- **Query Parameters**:
  - `q`: 검색어 (최소 2글자)
  - `limit`: 결과 개수 (기본 10개, 최대 50개)

## 📝 응답 형식

```json
{
  "success": true,
  "data": {
    "results": [
      {
        "apt_id": "...",
        "apt_name": "...",
        "address": "...",
        "sigungu_name": "...",
        "dong_name": "...",
        "location": {
          "lat": 37.123456,
          "lng": 127.123456
        }
      }
    ]
  },
  "meta": {
    "query": "래미안",
    "count": 10
  }
}
```

## ⚠️ 주의사항

### 네트워크 연결

- **로컬 개발**: `localhost:8000` 사용
- **Android 에뮬레이터**: `10.0.2.2:8000` 사용
- **iOS 시뮬레이터**: `localhost:8000` 사용
- **실제 디바이스**: 컴퓨터의 IP 주소 사용 (예: `192.168.0.100:8000`)

### CORS 설정

백엔드 서버에서 CORS를 허용해야 합니다:

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경만
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🐛 문제 해결

### 연결 오류 발생 시

1. 백엔드 서버가 실행 중인지 확인
2. API 주소가 올바른지 확인
3. 방화벽 설정 확인
4. 네트워크 연결 확인

### Android 에뮬레이터에서 연결 안 될 때

`localhost` 대신 `10.0.2.2` 사용:
```typescript
const API_BASE_URL = 'http://10.0.2.2:8000/api/v1/search';
```
