"""
Test API Endpoints - Redis 가짜 데이터 테스트용 API

이 엔드포인트들은 실제 DB 대신 Redis를 사용하여 API 동작을 테스트합니다.
사용자 → API → Redis(가짜 데이터) 흐름을 테스트할 수 있습니다.

사용법:
    1. Redis 실행: docker-compose up -d redis
    2. 가짜 데이터 로드: python api-test/scripts/load_mock_data.py
    3. 서버 실행: uvicorn app.main:app --reload
    4. API 테스트: http://localhost:8000/api/v1/test/
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Redis 서비스 (연결 실패시 Mock 데이터 사용)
try:
    from app.services.redis_service import get_redis_service
    USE_REDIS = True
except ImportError:
    USE_REDIS = False


router = APIRouter()


# ============== Pydantic 모델 ==============

class TodoBase(BaseModel):
    title: str
    completed: bool = False
    priority: str = "medium"


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None


class TodoResponse(TodoBase):
    id: str
    created_at: str
    updated_at: str


class ApartmentResponse(BaseModel):
    id: str
    name: str
    address: str
    price: int
    size_sqm: float
    rooms: int
    bathrooms: int
    floor: int
    total_floors: int
    built_year: int
    available: bool


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar: str


class HealthResponse(BaseModel):
    status: str
    redis_connected: bool
    message: str


# ============== 헬스 체크 ==============

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    API 및 Redis 연결 상태 확인
    
    Returns:
        status: API 상태
        redis_connected: Redis 연결 여부
        message: 상태 메시지
    """
    if USE_REDIS:
        redis_svc = get_redis_service()
        connected = redis_svc.connect()
        return HealthResponse(
            status="ok",
            redis_connected=connected,
            message="Redis 연결됨" if connected else "Redis 연결 실패 - Mock 모드로 동작"
        )
    return HealthResponse(
        status="ok",
        redis_connected=False,
        message="Redis 서비스 없음 - Mock 모드로 동작"
    )


# ============== TODO API ==============

@router.get("/todos", response_model=List[TodoResponse], tags=["Todos"])
async def get_todos():
    """
    모든 할 일 목록 조회 (Redis에서 가짜 데이터 불러옴)
    
    Returns:
        할 일 목록
    """
    if USE_REDIS:
        redis_svc = get_redis_service()
        if redis_svc.connect():
            return redis_svc.get_all_todos()
    
    # Fallback: Mock 데이터 직접 반환
    return [
        {
            "id": "mock-001",
            "title": "[Mock] 테스트 할 일",
            "completed": False,
            "priority": "high",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]


@router.get("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def get_todo(todo_id: str):
    """특정 할 일 조회"""
    if USE_REDIS:
        redis_svc = get_redis_service()
        if redis_svc.connect():
            todo = redis_svc.get_todo(todo_id)
            if todo:
                return todo
    
    raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다")


@router.post("/todos", response_model=TodoResponse, tags=["Todos"])
async def create_todo(todo: TodoCreate):
    """새 할 일 생성"""
    new_todo = {
        "id": f"todo-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "title": todo.title,
        "completed": todo.completed,
        "priority": todo.priority,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    if USE_REDIS:
        redis_svc = get_redis_service()
        if redis_svc.connect():
            return redis_svc.create_todo(new_todo)
    
    return new_todo


@router.put("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def update_todo(todo_id: str, todo: TodoUpdate):
    """할 일 수정"""
    update_data = {k: v for k, v in todo.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now().isoformat()
    
    if USE_REDIS:
        redis_svc = get_redis_service()
        if redis_svc.connect():
            updated = redis_svc.update_todo(todo_id, update_data)
            if updated:
                return updated
    
    raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다")


@router.delete("/todos/{todo_id}", tags=["Todos"])
async def delete_todo(todo_id: str):
    """할 일 삭제"""
    if USE_REDIS:
        redis_svc = get_redis_service()
        if redis_svc.connect():
            if redis_svc.delete_todo(todo_id):
                return {"message": "삭제 완료", "id": todo_id}
    
    raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다")


# ============== APARTMENT API ==============

@router.get("/apartments", response_model=List[ApartmentResponse], tags=["Apartments"])
async def get_apartments(
    min_price: Optional[int] = Query(None, description="최소 가격"),
    max_price: Optional[int] = Query(None, description="최대 가격"),
    min_size: Optional[float] = Query(None, description="최소 면적 (㎡)"),
    rooms: Optional[int] = Query(None, description="방 개수")
):
    """
    아파트 목록 조회 (필터링 지원)
    
    Args:
        min_price: 최소 가격
        max_price: 최대 가격
        min_size: 최소 면적
        rooms: 방 개수
    """
    if USE_REDIS:
        redis_svc = get_redis_service()
        if redis_svc.connect():
            return redis_svc.search_apartments(
                min_price=min_price,
                max_price=max_price,
                min_size=min_size,
                rooms=rooms
            )
    
    return []


@router.get("/apartments/{apt_id}", response_model=ApartmentResponse, tags=["Apartments"])
async def get_apartment(apt_id: str):
    """특정 아파트 조회"""
    if USE_REDIS:
        redis_svc = get_redis_service()
        if redis_svc.connect():
            apt = redis_svc.get_apartment(apt_id)
            if apt:
                return apt
    
    raise HTTPException(status_code=404, detail="아파트를 찾을 수 없습니다")


# ============== USER API ==============

@router.get("/users", response_model=List[UserResponse], tags=["Users"])
async def get_users():
    """모든 사용자 목록 조회"""
    if USE_REDIS:
        redis_svc = get_redis_service()
        if redis_svc.connect():
            return redis_svc.get_all_users()
    
    return []


@router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(user_id: str):
    """특정 사용자 조회"""
    if USE_REDIS:
        redis_svc = get_redis_service()
        if redis_svc.connect():
            user = redis_svc.get_user(user_id)
            if user:
                return user
    
    raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
