from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List

class SubscriptionCreate(BaseModel):
    target_url: str
    secret: Optional[str]

class SubscriptionOut(BaseModel):
    id: int
    target_url: str
    secret: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class DeliveryCreate(BaseModel):
    subscription_id: int
    payload: str

class DeliveryOut(BaseModel):
    id: int
    subscription_id: int
    payload: str
    status: str
    attempts: int
    last_error: Optional[str]

    class Config:
        orm_mode = True

class DeliveryList(BaseModel):
    deliveries: List[DeliveryOut]