from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas
import crud
from database import get_db

router = APIRouter(prefix="/api/items", tags=["藏品档案"])


@router.get("", response_model=schemas.ItemPage)
def list_items(
    page: int = 1,
    page_size: int = 10,
    series: str = None,
    rarity: str = None,
    keyword: str = None,
    db: Session = Depends(get_db),
):
    return crud.get_items(db, page, page_size, series, rarity, keyword)


@router.get("/series", response_model=list[str])
def list_series(db: Session = Depends(get_db)):
    return crud.get_all_series(db)


@router.get("/{item_id}", response_model=schemas.ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="藏品不存在")
    return item


@router.post("", response_model=schemas.ItemOut, status_code=201)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db, item)


@router.put("/{item_id}", response_model=schemas.ItemOut)
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    result = crud.update_item(db, item_id, item)
    if not result:
        raise HTTPException(status_code=404, detail="藏品不存在")
    return result


@router.delete("/{item_id}", response_model=schemas.ItemOut)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    result = crud.soft_delete_item(db, item_id)
    if not result:
        raise HTTPException(status_code=404, detail="藏品不存在")
    return result
