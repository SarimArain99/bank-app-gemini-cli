from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Dummy database
db = {
    "user_1": {
        "account_balance": 10000,
        "correct_pin": "1234",
        "pin_verified": False,
    },
    "user_2": {
        "account_balance": 5000,
        "raast_id": "0000",
    }
}

class Pin(BaseModel):
    pin: str

class Withdrawal(BaseModel):
    amount: int

class ShareBalance(BaseModel):
    recipient_id: str
    amount: int

@app.post("/verify_pin")
async def verify_pin(pin: Pin):
    if pin.pin == db["user_1"]["correct_pin"]:
        db["user_1"]["pin_verified"] = True
        return {
            "message": "PIN verified. Welcome!",
            "menu": [
                "1. Show balance",
                "2. Fast cash (500, 1000, 5000)",
                "3. Withdraw a custom amount",
                "4. Share balance",
                "5. Exit",
            ],
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid PIN")

@app.get("/balance")
async def get_balance():
    if not db["user_1"]["pin_verified"]:
        raise HTTPException(status_code=403, detail="PIN not verified")
    return {"balance": db["user_1"]["account_balance"]}

@app.post("/fast_cash")
async def fast_cash(withdrawal: Withdrawal):
    if not db["user_1"]["pin_verified"]:
        raise HTTPException(status_code=403, detail="PIN not verified")
    
    amount = withdrawal.amount
    if amount not in [500, 1000, 5000]:
        raise HTTPException(status_code=400, detail="Invalid fast cash amount")

    if db["user_1"]["account_balance"] < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    db["user_1"]["account_balance"] -= amount
    return {"message": f"Withdrew {amount}. Remaining balance: {db['user_1']['account_balance']}"}

@app.post("/withdraw")
async def withdraw(withdrawal: Withdrawal):
    if not db["user_1"]["pin_verified"]:
        raise HTTPException(status_code=403, detail="PIN not verified")

    amount = withdrawal.amount
    if db["user_1"]["account_balance"] < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    db["user_1"]["account_balance"] -= amount
    return {"message": f"Withdrew {amount}. Remaining balance: {db['user_1']['account_balance']}"}

@app.post("/share_balance")
async def share_balance(share: ShareBalance):
    if not db["user_1"]["pin_verified"]:
        raise HTTPException(status_code=403, detail="PIN not verified")

    if share.recipient_id != db["user_2"]["raast_id"]:
        raise HTTPException(status_code=404, detail="Recipient not found")

    if db["user_1"]["account_balance"] < share.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    db["user_1"]["account_balance"] -= share.amount
    db["user_2"]["account_balance"] += share.amount
    return {
        "message": f"Successfully shared {share.amount} with {share.recipient_id}. "
                   f"Your remaining balance is: {db['user_1']['account_balance']}"
    }

@app.get("/exit")
async def exit_app():
    db["user_1"]["pin_verified"] = False
    return {"message": "Goodbye!"}