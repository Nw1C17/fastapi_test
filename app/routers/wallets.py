from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/v1/wallets", tags=["wallets"])

@router.post("/", response_model=schemas.WalletCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(db: AsyncSession = Depends(get_db)):
    wallet = await crud.create_wallet(db)
    return {"uuid": wallet.uuid}

@router.post("/{wallet_uuid}/operation", response_model=schemas.WalletResponse)
async def perform_operation(
    wallet_uuid: UUID,
    operation: schemas.OperationRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        wallet = await crud.update_balance(db, wallet_uuid, operation.amount, operation.operation_type.value)
    except ValueError as e:
        if str(e) == "Кошелек не найден":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Кошелек не найден")
        elif str(e) == "Insufficient funds":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
        raise
    return {"uuid": wallet.uuid, "balance": wallet.balance}

@router.get("/{wallet_uuid}", response_model=schemas.WalletResponse)
async def get_balance(wallet_uuid: UUID, db: AsyncSession = Depends(get_db)):
    wallet = await crud.get_wallet(db, wallet_uuid)
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="кошелек не найден")
    return {"uuid": wallet.uuid, "balance": wallet.balance}