from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas
import crud
from database import get_db

router = APIRouter(prefix="/api/recycle", tags=["回收站"])


@router.get("", response_model=schemas.RecyclePage)
def list_recycle(db: Session = Depends(get_db)):
    return crud.get_recycle_bin(db)


@router.post("/items/{item_id}/restore", response_model=schemas.ItemOut)
def restore_item(item_id: int, db: Session = Depends(get_db)):
    result = crud.restore_item(db, item_id)
    if not result:
        raise HTTPException(status_code=404, detail="回收站中未找到该藏品")
    return result


@router.post("/exchanges/{exchange_id}/restore", response_model=schemas.ExchangeOut)
def restore_exchange(exchange_id: int, db: Session = Depends(get_db)):
    result = crud.restore_exchange(db, exchange_id)
    if not result:
        raise HTTPException(status_code=404, detail="回收站中未找到该置换记录")
    ex_out = schemas.ExchangeOut.model_validate(result)
    if result.item:
        ex_out.item_series = result.item.series
        ex_out.item_name = result.item.name
    return ex_out


@router.delete("/items/{item_id}")
def hard_delete_item(item_id: int, db: Session = Depends(get_db)):
    if not crud.hard_delete_item(db, item_id):
        raise HTTPException(status_code=404, detail="仅可永久删除已在回收站的藏品")
    return {"message": "已永久删除"}


@router.delete("/exchanges/{exchange_id}")
def hard_delete_exchange(exchange_id: int, db: Session = Depends(get_db)):
    if not crud.hard_delete_exchange(db, exchange_id):
        raise HTTPException(status_code=404, detail="仅可永久删除已在回收站的置换记录")
    return {"message": "已永久删除"}
