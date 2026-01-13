"""
아파트명 검색 API 엔드포인트

담당자: 박찬영
담당 기능:
- 아파트명 검색 (GET /search/apartments) - P0
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
import re

# Redis 서비스 (연결 실패시 Mock 데이터 사용)
try:
    from app.services.redis_service import get_redis_service
    USE_REDIS = True
except ImportError:
    USE_REDIS = False

router = APIRouter()


@router.get(
    "/apartments",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    tags=["🔍 Search (검색)"],
    summary="아파트명 검색 (자동완성)",
    description="아파트명으로 검색합니다. 검색창에 2글자 이상 입력 시 자동완성 결과를 반환합니다."
)
async def search_apartments(
    q: str = Query(
        ..., 
        min_length=2, 
        description="검색어 (2글자 이상)",
        example="래미안"
    ),
    limit: int = Query(
        10, 
        ge=1, 
        le=50, 
        description="결과 개수 (기본 10개, 최대 50개)"
    )
):
    """
    ## 아파트명 검색 API
    
    검색창에 입력한 글자를 포함하는 아파트 목록을 반환합니다.
    Redis 더미데이터를 사용하여 검색합니다.
    
    ### Query Parameters
    - **q**: 검색어 (최소 2글자)
    - **limit**: 반환할 결과 개수 (기본 10개, 최대 50개)
    
    ### Response
    - 성공: 아파트 목록 (이름, 주소, 위치 정보)
    - 실패: 422 (검색어가 2글자 미만)
    """
    # Redis 캐시에서 아파트 데이터 가져오기
    # 실제 DB 수정 중이므로 Redis 캐시를 사용하여 가짜 데이터 제공
    # Redis가 없으면 JSON 파일에서 직접 로드
    apartments_data = []
    
    if USE_REDIS:
        try:
            redis_svc = get_redis_service()
            if redis_svc.connect():
                # Redis 서비스의 검색 메서드 사용
                apartments_data = redis_svc.search_apartments_by_name(q, limit)
        except Exception as e:
            # Redis 연결 실패시 JSON 파일에서 직접 로드
            apartments_data = []
    
    # Redis에 데이터가 없으면 JSON 파일에서 직접 로드
    if not apartments_data:
        try:
            import json
            from pathlib import Path
            
            # mock-data 폴더 경로 찾기
            current_file = Path(__file__)
            mock_data_path = current_file.parent.parent.parent.parent.parent.parent / "api-test" / "mock-data" / "apartments.json"
            
            if mock_data_path.exists():
                with open(mock_data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # JSON 파일이 {"apartments": [...]} 형식인 경우
                    if isinstance(data, dict) and "apartments" in data:
                        all_apartments = data["apartments"]
                    # 이미 리스트인 경우
                    elif isinstance(data, list):
                        all_apartments = data
                    else:
                        all_apartments = []
                    
                    # 검색어로 필터링
                    query_lower = q.lower()
                    filtered = [
                        apt for apt in all_apartments
                        if query_lower in apt.get("apt_name", "").lower()
                    ]
                    filtered.sort(key=lambda x: x.get("apt_name", ""))
                    apartments_data = filtered[:limit]
        except Exception as e:
            # 파일 로드 실패시 빈 리스트
            apartments_data = []
    
    # 응답 데이터 구성 (실제 DB 구조와 동일한 형식)
    # search_apart.py의 응답 형식에 맞춤
    results = []
    for apt in apartments_data:
        result_item = {
            "apt_id": apt.get("apt_id"),
            "apt_name": apt.get("apt_name", ""),
            "address": apt.get("address", ""),
            "sigungu_name": apt.get("sigungu_name"),
            "dong_name": apt.get("dong_name"),
        }
        
        # 위치 정보 추가 (latitude, longitude가 있으면)
        if apt.get("latitude") and apt.get("longitude"):
            result_item["location"] = {
                "lat": apt.get("latitude"),
                "lng": apt.get("longitude")
            }
        else:
            result_item["location"] = None
        
        results.append(result_item)
    
    return {
        "success": True,
        "data": {
            "results": results
        },
        "meta": {
            "query": q,
            "count": len(results)
        }
    }


@router.get(
    "/locations",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    tags=["🔍 Search (검색)"],
    summary="지역 검색",
    description="지역명(시/군/구/동)으로 검색합니다. 시군구 또는 동 단위로 검색할 수 있습니다.",
    responses={
        200: {"description": "검색 성공"},
        422: {"description": "입력값 검증 실패"}
    }
)
async def search_locations(
    q: str = Query(..., min_length=1, description="검색어"),
    location_type: Optional[str] = Query(
        None, 
        regex="^(sigungu|dong)$",
        description="지역 유형 (sigungu: 시군구, dong: 동)"
    )
):
    """
    지역 검색 API
    
    시/군/구 또는 동 단위로 지역을 검색합니다.
    검색어로 시작하거나 포함하는 지역 목록을 반환합니다.
    
    Args:
        q: 검색어
        location_type: 지역 유형 필터 (sigungu: 시군구, dong: 동, None: 전체)
        db: 데이터베이스 세션
    
    Returns:
        {
            "success": true,
            "data": {
                "results": [
                    {
                        "id": int,
                        "name": str,
                        "type": str,
                        "full_name": str,
                        "center": {"lat": float, "lng": float}
                    }
                ]
            }
        }
    
    Note:
        - location_type이 None이면 시군구와 동 모두 검색
        - Redis 캐싱 적용 권장 (TTL: 1시간)
    """
    # TODO: SearchService.search_locations() 구현 후 사용
    # result = await SearchService.search_locations(db, query=q, location_type=location_type)
    
    # 임시 응답 (서비스 레이어 구현 전)
    return {
        "success": True,
        "data": {
            "results": []
        }
    }


@router.get(
    "/recent",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    tags=["🔍 Search (검색)"],
    summary="최근 검색어 조회",
    description="로그인한 사용자의 최근 검색어 목록을 조회합니다. 검색창을 탭했을 때 이전 검색 기록을 보여줍니다.",
    responses={
        200: {"description": "조회 성공"},
        401: {"description": "로그인이 필요합니다"}
    }
)
async def get_recent_searches(
    limit: int = Query(10, ge=1, le=50, description="최대 개수 (기본 10개, 최대 50개)")
):
    """
    최근 검색어 조회 API
    
    로그인한 사용자가 최근에 검색한 기록을 시간순(최신순)으로 반환합니다.
    아파트 검색과 지역 검색을 모두 포함합니다.
    
    Args:
        limit: 반환할 최대 개수 (기본 10개, 최대 50개)
        current_user: 현재 로그인한 사용자 (의존성 주입)
        db: 데이터베이스 세션
    
    Returns:
        {
            "success": true,
            "data": {
                "recent_searches": [
                    {
                        "id": int,
                        "query": str,
                        "type": str,  # "apartment" 또는 "location"
                        "searched_at": str  # ISO 8601 형식
                    }
                ]
            }
        }
    
    Raises:
        HTTPException: 로그인이 필요한 경우 401 에러
    """
    # TODO: SearchService.get_recent_searches() 구현 후 사용
    # result = await SearchService.get_recent_searches(db, user_id=current_user.id, limit=limit)
    
    # 임시 응답 (서비스 레이어 구현 전)
    return {
        "success": True,
        "data": {
            "recent_searches": []
        }
    }


@router.delete(
    "/recent/{search_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    tags=["🔍 Search (검색)"],
    summary="최근 검색어 삭제",
    description="특정 최근 검색어를 삭제합니다. 사용자가 검색 기록을 개별적으로 삭제할 때 사용합니다.",
    responses={
        200: {"description": "삭제 성공"},
        401: {"description": "로그인이 필요합니다"},
        404: {"description": "검색어를 찾을 수 없습니다"}
    }
)
async def delete_recent_search(
    search_id: int
):
    """
    최근 검색어 삭제 API
    
    로그인한 사용자의 특정 검색 기록을 삭제합니다.
    본인의 검색 기록만 삭제할 수 있습니다.
    
    Args:
        search_id: 삭제할 검색어 ID
        current_user: 현재 로그인한 사용자 (의존성 주입)
        db: 데이터베이스 세션
    
    Returns:
        {
            "success": true,
            "data": {
                "message": "검색어가 삭제되었습니다."
            }
        }
    
    Raises:
        HTTPException: 
            - 401: 로그인이 필요한 경우
            - 404: 검색어를 찾을 수 없거나 본인의 검색 기록이 아닌 경우
    """
    # TODO: SearchService.delete_recent_search() 구현 후 사용
    # await SearchService.delete_recent_search(db, search_id=search_id, user_id=current_user.id)
    
    # 임시 응답 (서비스 레이어 구현 전)
    return {
        "success": True,
        "data": {
            "message": "검색어가 삭제되었습니다."
        }
    }
