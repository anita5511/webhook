from fastapi import FastAPI
from api.routers import subscriptions, deliveries

app = FastAPI(title="Webhook Delivery Service")
app.include_router(subscriptions.router)
app.include_router(deliveries.router)