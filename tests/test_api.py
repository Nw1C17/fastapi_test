import pytest
import asyncio
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_deposit_and_withdraw(client: AsyncClient):
    # Создаём кошелёк
    create_resp = await client.post("/api/v1/wallets/")
    assert create_resp.status_code == 201
    wallet_uuid = create_resp.json()["uuid"]

    # Пополнение (10000 копеек = 100.00)
    dep_resp = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": 10000}
    )
    assert dep_resp.status_code == 200
    assert dep_resp.json()["balance"] == 10000

    # Снятие (5025 копеек)
    wit_resp = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "WITHDRAW", "amount": 5025}
    )
    assert wit_resp.status_code == 200
    assert wit_resp.json()["balance"] == 4975

    # Проверка баланса
    bal_resp = await client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert bal_resp.status_code == 200
    assert bal_resp.json()["balance"] == 4975

@pytest.mark.asyncio
async def test_insufficient_funds(client: AsyncClient):
    create_resp = await client.post("/api/v1/wallets/")
    wallet_uuid = create_resp.json()["uuid"]

    await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": 1000}
    )
    resp = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "WITHDRAW", "amount": 2000}
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Insufficient funds"

@pytest.mark.asyncio
async def test_wallet_not_found(client: AsyncClient):
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    resp = await client.get(f"/api/v1/wallets/{fake_uuid}")
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_concurrent_operations(client: AsyncClient):
    create_resp = await client.post("/api/v1/wallets/")
    wallet_uuid = create_resp.json()["uuid"]

    await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": 100000}
    )

    async def withdraw(amount):
        async with AsyncClient(transport=client._transport, base_url="http://test") as c:
            return await c.post(
                f"/api/v1/wallets/{wallet_uuid}/operation",
                json={"operation_type": "WITHDRAW", "amount": amount}
            )

    tasks = [withdraw(20000) for _ in range(5)]
    responses = await asyncio.gather(*tasks)
    assert all(r.status_code == 200 for r in responses)

    final = await client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert final.json()["balance"] == 0

    # Попытка снять больше — хотя бы одна ошибка
    tasks_over = [withdraw(20000) for _ in range(6)]
    results = await asyncio.gather(*tasks_over, return_exceptions=True)
    assert any(isinstance(r, Exception) or (hasattr(r, 'status_code') and r.status_code == 400) for r in results)
    final_balance = await client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert final_balance.json()["balance"] >= 0