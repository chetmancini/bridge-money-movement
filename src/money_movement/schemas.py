from pydantic import BaseModel


class TransferRequest(BaseModel):
    investor_id: int
    fund_id: int
    amount: float


class TransferStatus(BaseModel):
    status: str
    message: str
