from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas
import crud
from database import get_db

router = APIRouter(prefix="/api/market-prices", tags=["行情参考价"])


@router.get("", response_model=schemas.MarketPricePage)
def list_market_prices(
    page: int = 1,
    page_size: int = 10,
    style_id: str = None,
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db),
):
    return crud.get_market_prices(db, page, page_size, style_id, date_from, date_to)


@router.get("/trend/{style_id}", response_model=schemas.MarketPriceTrend)
def get_market_trend(
    style_id: str,
    purchase_price: float = None,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return crud.get_market_trend(db, style_id, limit, purchase_price)


@router.get("/{price_id}", response_model=schemas.MarketPriceOut)
def get_market_price(price_id: int, db: Session = Depends(get_db)):
    price = crud.get_market_price(db, price_id)
    if not price:
        raise HTTPException(status_code=404, detail="行情记录不存在")
    return price


@router.post("", response_model=schemas.MarketPriceOut, status_code=201)
def create_market_price(price: schemas.MarketPriceCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_market_price(db, price)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{price_id}", response_model=schemas.MarketPriceOut)
def update_market_price(
    price_id: int, price: schemas.MarketPriceUpdate, db: Session = Depends(get_db)
):
    try:
        result = crud.update_market_price(db, price_id, price)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="行情记录不存在")
    return result


@router.delete("/{price_id}", response_model=schemas.MarketPriceOut)
def delete_market_price(price_id: int, db: Session = Depends(get_db)):
    result = crud.soft_delete_market_price(db, price_id)
    if not result:
        raise HTTPException(status_code=404, detail="行情记录不存在")
    return result
