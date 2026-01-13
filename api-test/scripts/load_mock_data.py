"""
Mock Data Loader - 가짜 데이터를 Redis에 로드하는 스크립트

사용법:
    python load_mock_data.py

이 스크립트는 mock-data 폴더의 JSON 파일들을 Redis에 로드합니다.
API 테스트 전에 실행하여 테스트 데이터를 준비합니다.
"""

import json
import redis
import sys
from pathlib import Path

# Windows 호환성을 위한 UTF-8 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_mock_data_to_redis(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    redis_db: int = 0
):
    """
    mock-data 폴더의 JSON 파일들을 Redis에 로드
    
    Args:
        redis_host: Redis 서버 호스트
        redis_port: Redis 서버 포트
        redis_db: Redis DB 번호
    """
    # Redis 연결
    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        decode_responses=True
    )
    
    # 연결 테스트
    try:
        r.ping()
        print("[OK] Redis 연결 성공!")
    except redis.ConnectionError as e:
        print(f"[ERROR] Redis 연결 실패: {e}")
        print("\n[INFO] Redis가 실행 중인지 확인해주세요:")
        print("   docker-compose up -d redis")
        return False
    
    # mock-data 폴더 경로
    mock_data_dir = Path(__file__).parent.parent / "mock-data"
    
    # JSON 파일들 로드
    data_files = {
        "todos": "todos.json",
        "users": "users.json",
        "apartments": "apartments.json"
    }
    
    loaded_count = 0
    
    for key, filename in data_files.items():
        file_path = mock_data_dir / filename
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # JSON 파일 내부의 키로 데이터 접근 (예: {"todos": [...]} → [...])
                if key in data:
                    r.set(key, json.dumps(data[key]))
                    print(f"[OK] {filename} 로드 완료 ({len(data[key])}개 항목)")
                    loaded_count += 1
                else:
                    r.set(key, json.dumps(data))
                    print(f"[OK] {filename} 로드 완료")
                    loaded_count += 1
        else:
            print(f"[WARN] {filename} 파일을 찾을 수 없습니다")
    
    print(f"\n[SUCCESS] 총 {loaded_count}개 데이터셋 로드 완료!")
    print("\n📝 로드된 데이터 확인:")
    
    # 로드된 데이터 요약
    for key in data_files.keys():
        data = r.get(key)
        if data:
            items = json.loads(data)
            print(f"   - {key}: {len(items)}개")
    
    return True


def clear_redis_data(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    redis_db: int = 0
):
    """Redis 데이터 초기화"""
    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        decode_responses=True
    )
    
    keys = ["todos", "users", "apartments"]
    for key in keys:
        r.delete(key)
    
    print("[OK] Redis 데이터 초기화 완료!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        clear_redis_data()
    else:
        load_mock_data_to_redis()
