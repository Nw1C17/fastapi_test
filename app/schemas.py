from pydantic import BaseModel, Field
from uuid import UUID
from enum import Enum

class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

class OperationRequest(BaseModel):
    operation_type: OperationType
    amount: int = Field(..., gt=0, description="Сумма в центах (положительное целое число)")

class WalletResponse(BaseModel):
    uuid: UUID
    balance: int

class WalletCreateResponse(BaseModel):
    uuid: UUID