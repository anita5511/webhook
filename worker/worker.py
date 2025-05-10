import os
import time

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import hmac
import hashlib
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models import Base, Delivery, Subscription



DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

MAX_RETRIES = 5
INITIAL_BACKOFF = 2  # seconds


def process_delivery(delivery_id: int):
    db = SessionLocal()
    try:
        delivery = db.get(Delivery, delivery_id)
        sub = db.get(Subscription, delivery.subscription_id)
        headers = {'Content-Type': 'application/json'}
        body = delivery.payload
        # sign if secret
        if sub.secret:
            signature = hmac.new(sub.secret.encode(), body.encode(), hashlib.sha256).hexdigest()
            headers['X-Signature'] = signature

        success = False
        backoff = INITIAL_BACKOFF
        for attempt in range(delivery.attempts, MAX_RETRIES):
            try:
                resp = requests.post(sub.target_url, data=body, headers=headers, timeout=10)
                if resp.status_code < 300:
                    success = True
                    break
                else:
                    raise Exception(f"Status {resp.status_code}")
            except Exception as e:
                delivery.attempts += 1
                delivery.last_error = str(e)
                db.commit()
                time.sleep(backoff)
                backoff *= 2

        delivery.status = 'success' if success else 'failed'
        db.commit()
    finally:
        db.close()