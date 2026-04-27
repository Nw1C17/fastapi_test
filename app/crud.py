from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Wallet
from uuid import UUID

async def create_wallet(db: AsyncSession) -> Wallet:
    wallet = Wallet()
    db.add(wallet)
    await db.commit()
    await db.refresh(wallet)
    return wallet

async def get_wallet(db: AsyncSession, wallet_uuid: UUID):
    result = await db.execute(select(Wallet).where(Wallet.uuid == wallet_uuid))
    return result.scalar_one_or_none()

async def update_balance(db: AsyncSession, wallet_uuid: UUID, amount: int, operation_type: str) -> Wallet:
    # Блокировка строки для конкурентных обновлений
    result = await db.execute(
        select(Wallet).where(Wallet.uuid == wallet_uuid).with_for_update()
    )
    wallet = result.scalar_one_or_none()
    if not wallet:
        raise ValueError("кошелек не найден")

    if operation_type == "DEPOSIT":
        wallet.balance += amount
    elif operation_type == "WITHDRAW":
        if wallet.balance < amount:
            raise ValueError("Insufficient funds")
        wallet.balance -= amount

    await db.commit()
    await db.refresh(wallet)
    return wallet