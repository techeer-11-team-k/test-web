"""
데이터베이스 세션 관리

비동기 SQLAlchemy 세션을 생성하고 관리합니다.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# 비동기 엔진 생성
# connect_args에 connect_timeout을 설정하여 연결 실패 시 빠르게 실패하도록 함
try:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,  # 디버그 모드에서 SQL 쿼리 로그 출력
        future=True,
        pool_pre_ping=True,  # 연결 전에 ping을 보내서 연결 상태 확인
        connect_args={
            "server_settings": {
                "application_name": "realestate_backend"
            }
        }
    )
    logger.info("✅ 데이터베이스 엔진 생성 완료")
except Exception as e:
    logger.warning(f"⚠️ 데이터베이스 엔진 생성 중 오류 (연결은 나중에 시도됨): {e}")
    # 엔진 생성 실패 시에도 엔진 객체는 생성하되, 실제 연결은 나중에 시도
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True
    )

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)
