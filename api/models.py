from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True, index=True)
    target_url = Column(String, nullable=False)
    secret = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deliveries = relationship("Delivery", back_populates="subscription")

class Delivery(Base):
    __tablename__ = 'deliveries'
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'), nullable=False)
    payload = Column(Text, nullable=False)
    status = Column(String, default='pending')  # pending, success, failed
    attempts = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    subscription = relationship("Subscription", back_populates="deliveries")