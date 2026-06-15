from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas
import crud
from database import get_db

router = APIRouter(prefix="/api/exchanges", tags=["置换记录"])


@router.get("", response_model=schemas.ExchangePage)
def list_exchanges(
    page: int = 1,
    page_size: int = 10,
    counterparty: str = None,
    db: Session = Depends(get_db),
):
    return crud.get_exchanges(db, page, page_size, counterparty)


@router.get("/{exchange_id}", response_model=schemas.ExchangeOut)
def get_exchange(exchange_id: int, db: Session = Depends(get_db)):
    exchange = crud.get_exchange(db, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="置换记录不存在")
    ex_out = schemas.ExchangeOut.model_validate(exchange)
    if exchange.item:
        ex_out.item_series = exchange.item.series
        ex_out.item_name = exchange.item.name
    return ex_out


@router.post("", response_model=schemas.ExchangeOut, status_code=201)
def create_exchange(
    exchange: schemas.ExchangeCreate, db: Session = Depends(get_db)
):
    item = crud.get_item(db, exchange.item_id)
    if not item:
        raise HTTPException(status_code=400, detail="关联藏品不存在")
    db_exchange = crud.create_exchange(db, exchange)
    ex_out = schemas.ExchangeOut.model_validate(db_exchange)
    ex_out.item_series = item.series
    ex_out.item_name = item.name
    return ex_out


@router.put("/{exchange_id}", response_model=schemas.ExchangeOut)
def update_exchange(
    exchange_id: int,
    exchange: schemas.ExchangeUpdate,
    db: Session = Depends(get_db),
):
    if exchange.item_id is not None:
        item = crud.get_item(db, exchange.item_id)
        if not item:
            raise HTTPException(status_code=400, detail="关联藏品不存在")
    result = crud.update_exchange(db, exchange_id, exchange)
    if not result:
        raise HTTPException(status_code=404, detail="置换记录不存在")
    ex_out = schemas.ExchangeOut.model_validate(result)
    if result.item:
        ex_out.item_series = result.item.series
        ex_out.item_name = result.item.name
    return ex_out


@router.delete("/{exchange_id}", response_model=schemas.ExchangeOut)
def delete_exchange(exchange_id: int, db: Session = Depends(get_db)):
    result = crud.soft_delete_exchange(db, exchange_id)
    if not result:
        raise HTTPException(status_code=404, detail="置换记录不存在")
    ex_out = schemas.ExchangeOut.model_validate(result)
    if result.item:
        ex_out.item_series = result.item.series
        ex_out.item_name = result.item.name
    return ex_out
