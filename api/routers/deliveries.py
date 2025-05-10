from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api import models, schemas, dependencies, utils
from worker.worker import process_delivery

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])

@router.post("/", response_model=schemas.DeliveryOut, status_code=202)
def enqueue_delivery(
    payload: schemas.DeliveryCreate,
    db: Session = Depends(dependencies.get_db)
):
    sub = db.get(models.Subscription, payload.subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    delivery = models.Delivery(**payload.dict())
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    # enqueue background job
    utils.queue.enqueue(process_delivery, delivery.id)
    return delivery

@router.get("/subscription/{sub_id}", response_model=schemas.DeliveryList)
def list_deliveries(sub_id: int, db: Session = Depends(dependencies.get_db)):
    deliveries = db.query(models.Delivery).filter_by(subscription_id=sub_id).all()
    return {"deliveries": deliveries}