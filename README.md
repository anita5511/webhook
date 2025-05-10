# Webhook Delivery Service

This service lets clients subscribe webhook URLs and enqueue payload deliveries with retries and signing.

## Setup & Run Locally

1. **Build & run services** (web, worker, Postgres, Redis):
   ```bash
   docker-compose up --build -d