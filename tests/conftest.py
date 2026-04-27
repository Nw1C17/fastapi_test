import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.database import get_db
from app.models import Base
from app.config import settings

# Используем отдельную тестовую БД (можно переопределить через окружение)
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/wallet_test"

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
async def setup_db():
    # Создаём таблицы перед тестами
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Удаляем после тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(setup_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac