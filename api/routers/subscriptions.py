#api/routers/Subscription.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api import models, schemas, dependencies

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.post("/", response_model=schemas.SubscriptionOut, status_code=201)
def create_subscription(
    payload: schemas.SubscriptionCreate,
    db: Session = Depends(dependencies.get_db)
):
    sub = models.Subscription(**payload.dict())
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

@router.get("/{sub_id}", response_model=schemas.SubscriptionOut)
def get_subscription(sub_id: int, db: Session = Depends(dependencies.get_db)):
    sub = db.get(models.Subscription, sub_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Not found")
    return sub