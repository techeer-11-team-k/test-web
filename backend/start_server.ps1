# 서버 시작 스크립트
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/realestate"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:CLERK_SECRET_KEY = "sk_test_dummy"
$env:SECRET_KEY = "dev-secret-key"

Write-Host "환경변수 설정 완료"
Write-Host "서버 시작 중..."

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
