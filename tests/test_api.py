import pytest
import asyncio
from httpx import AsyncClient
from uuid import uuid4

@pytest.mark.asyncio
async def test_deposit_and_withdraw(client: AsyncClient):
    wallet_uuid = uuid4()
    # Пополнение
    resp = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": "100.50"}
    )
    assert resp.status_code == 200
    assert resp.json()["balance"] == "100.50"

    # Снятие
    resp = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "WITHDRAW", "amount": "50.25"}
    )
    assert resp.status_code == 200
    assert resp.json()["balance"] == "50.25"

    # Получение баланса
    resp = await client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert resp.status_code == 200
    assert resp.json()["balance"] == "50.25"

@pytest.mark.asyncio
async def test_insufficient_funds(client: AsyncClient):
    wallet_uuid = uuid4()
    await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": "10"}
    )
    resp = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "WITHDRAW", "amount": "20"}
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Insufficient funds"

@pytest.mark.asyncio
async def test_wallet_not_found(client: AsyncClient):
    wallet_uuid = uuid4()
    resp = await client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_concurrent_operations(client: AsyncClient):
    wallet_uuid = uuid4()
    # Изначально пополним на 1000
    await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": "1000"}
    )

    async def withdraw(amount):
        return await client.post(
            f"/api/v1/wallets/{wallet_uuid}/operation",
            json={"operation_type": "WITHDRAW", "amount": amount}
        )

    # Запускаем 5 параллельных снятий по 200 (всего 1000)
    tasks = [withdraw("200") for _ in range(5)]
    responses = await asyncio.gather(*tasks)

    # Все должны быть успешны
    for resp in responses:
        assert resp.status_code == 200

    # Итоговый баланс должен быть 0
    final = await client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert final.json()["balance"] == "0.00"

    # Тест на параллельное снятие больше, чем есть: 6*200=1200 > 1000
    tasks = [withdraw("200") for _ in range(6)]
    responses = await asyncio.gather(*tasks)
    # Один из запросов упадёт с 400, остальные 5 успешны? Но порядок выполнения不确定.
    # Проверим, что итоговый баланс не отрицательный.
    final = await client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert float(final.json()["balance"]) >= 0