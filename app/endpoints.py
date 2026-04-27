from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from decimal import Decimal
from app import schemas, crud
from app.database import get_db

router = APIRouter(prefix="/api/v1/wallets", tags=["wallets"])

@router.post("/{wallet_uuid}/operation", response_model=schemas.BalanceResponse)
async def perform_operation(
    wallet_uuid: UUID,
    operation: schemas.OperationRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        new_balance = await crud.update_wallet_balance(
            db, wallet_uuid, operation.amount, operation.operation_type
        )
        return schemas.BalanceResponse(balance=new_balance)
    except ValueError as e:
        if str(e) == "Wallet not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
        elif str(e) == "Insufficient funds":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{wallet_uuid}", response_model=schemas.BalanceResponse)
async def get_balance(
    wallet_uuid: UUID,
    db: AsyncSession = Depends(get_db)
):
    balance = await crud.get_wallet_balance(db, wallet_uuid)
    if balance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    return schemas.BalanceResponse(balance=balance)