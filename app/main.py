from fastapi import FastAPI
from app.routers import wallets

app = FastAPI(title="Wallet API", version="1.0")

app.include_router(wallets.router)