from fastapi import FastAPI, HTTPException

from money_movement.controller import process_new_transaction, transaction_status
from money_movement.models import TransactionState
from money_movement.schemas import TransferRequest, TransferStatus

app = FastAPI()


@app.post("/transfer", response_model=TransferStatus)
def initiate_transfer(request: TransferRequest):
    status, message = process_new_transaction(
        request.investor_id, request.fund_id, request.amount
    )
    if status == "success":
        return TransferStatus(status=status, message=message)
    elif status == "retry":
        # Logic to handle retry, could include a more sophisticated retry mechanism
        return TransferStatus(status="failure", message=message)
    else:
        raise HTTPException(status_code=400, detail=message)


@app.get("/transfer/{transfer_id}", response_model=TransferStatus)
def check_transfer_status(transfer_id: int):
    state: TransactionState = transaction_status(transfer_id)
    if state:
        return TransferStatus(
            status=state.value, message=f"Transaction is in state {state.value}"
        )
    else:
        raise HTTPException(status_code=404, detail="Transfer not found")
