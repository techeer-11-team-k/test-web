"""
Redis Service - 가짜 데이터 테스트용 Redis 서비스

이 서비스는 실제 DB 대신 Redis를 사용하여 API 테스트를 수행합니다.
사용자 → API → Redis(가짜 데이터) 흐름으로 테스트 가능
"""

import json
import redis
from typing import Optional, List, Dict, Any
from pathlib import Path


class RedisService:
    """Redis 연동 서비스 클래스"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """
        Redis 연결 초기화
        
        Args:
            host: Redis 서버 호스트
            port: Redis 서버 포트
            db: Redis DB 번호
        """
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        self._connected = False
    
    def connect(self) -> bool:
        """Redis 연결 테스트"""
        try:
            self.redis_client.ping()
            self._connected = True
            return True
        except redis.ConnectionError:
            self._connected = False
            return False
    
    @property
    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self._connected
    
    # ============== TODO 관련 메서드 ==============
    
    def get_all_todos(self) -> List[Dict[str, Any]]:
        """모든 할 일 목록 조회"""
        todos = self.redis_client.get("todos")
        if todos:
            return json.loads(todos)
        return []
    
    def get_todo(self, todo_id: str) -> Optional[Dict[str, Any]]:
        """특정 할 일 조회"""
        todos = self.get_all_todos()
        for todo in todos:
            if todo.get("id") == todo_id:
                return todo
        return None
    
    def create_todo(self, todo_data: Dict[str, Any]) -> Dict[str, Any]:
        """할 일 생성"""
        todos = self.get_all_todos()
        todos.append(todo_data)
        self.redis_client.set("todos", json.dumps(todos))
        return todo_data
    
    def update_todo(self, todo_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """할 일 수정"""
        todos = self.get_all_todos()
        for i, todo in enumerate(todos):
            if todo.get("id") == todo_id:
                todos[i].update(update_data)
                self.redis_client.set("todos", json.dumps(todos))
                return todos[i]
        return None
    
    def delete_todo(self, todo_id: str) -> bool:
        """할 일 삭제"""
        todos = self.get_all_todos()
        original_len = len(todos)
        todos = [t for t in todos if t.get("id") != todo_id]
        if len(todos) < original_len:
            self.redis_client.set("todos", json.dumps(todos))
            return True
        return False
    
    # ============== USER 관련 메서드 ==============
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """모든 사용자 목록 조회"""
        users = self.redis_client.get("users")
        if users:
            return json.loads(users)
        return []
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """특정 사용자 조회"""
        users = self.get_all_users()
        for user in users:
            if user.get("id") == user_id:
                return user
        return None
    
    # ============== APARTMENT 관련 메서드 ==============
    
    def get_all_apartments(self) -> List[Dict[str, Any]]:
        """
        모든 아파트 목록 조회 (Redis 캐시에서)
        
        실제 DB 구조와 동일한 형식으로 데이터를 반환합니다.
        """
        apartments_data = self.redis_client.get("apartments")
        if apartments_data:
            data = json.loads(apartments_data)
            # JSON 파일이 {"apartments": [...]} 형식인 경우
            if isinstance(data, dict) and "apartments" in data:
                return data["apartments"]
            # 이미 리스트인 경우
            elif isinstance(data, list):
                return data
        return []
    
    def get_apartment(self, apt_id: int) -> Optional[Dict[str, Any]]:
        """
        특정 아파트 조회 (apt_id로)
        
        Args:
            apt_id: 아파트 고유 ID (int)
        """
        apartments = self.get_all_apartments()
        for apt in apartments:
            if apt.get("apt_id") == apt_id:
                return apt
        return None
    
    def search_apartments_by_name(
        self,
        query: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        아파트명으로 검색 (자동완성용)
        
        Args:
            query: 검색어 (최소 2글자)
            limit: 최대 반환 개수
        
        Returns:
            검색된 아파트 목록 (이름순 정렬)
        """
        apartments = self.get_all_apartments()
        query_lower = query.lower()
        
        # 아파트명에 검색어가 포함된 항목 필터링
        results = [
            apt for apt in apartments
            if query_lower in apt.get("apt_name", "").lower()
        ]
        
        # 이름순으로 정렬
        results.sort(key=lambda x: x.get("apt_name", ""))
        
        # limit만큼 제한
        return results[:limit]


# 싱글톤 인스턴스
redis_service: Optional[RedisService] = None


def get_redis_service() -> RedisService:
    """Redis 서비스 인스턴스 반환"""
    global redis_service
    if redis_service is None:
        redis_service = RedisService()
    return redis_service
