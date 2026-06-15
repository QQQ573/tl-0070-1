from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from database import engine, Base
from migrate import run_migrations
from routers import items, exchanges, uploads, market_prices, stats, recycle

run_migrations()

app = FastAPI(
    title="Labubu 藏品管理系统",
    description="藏家 Labubu 藏品档案与置换记录管理",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(items.router)
app.include_router(exchanges.router)
app.include_router(uploads.router)
app.include_router(market_prices.router)
app.include_router(stats.router)
app.include_router(recycle.router)


@app.get("/")
def root():
    return {"message": "Labubu 藏品管理系统 API"}
