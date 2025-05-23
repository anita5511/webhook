# Webhook Delivery Service

A robust, production-ready webhook delivery system built with FastAPI, PostgreSQL, and Redis. This service enables reliable webhook delivery with automatic retries, payload signing, and delivery status tracking.

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs with Python
- **PostgreSQL**: Primary database for storing subscriptions and delivery records
- **Redis**: Message broker for handling asynchronous webhook deliveries
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **Alembic**: Database migration tool
- **RQ (Redis Queue)**: Library for queueing and processing background jobs
- **Docker & Docker Compose**: Containerization and service orchestration

## Features

- Create webhook subscriptions with optional payload signing
- Enqueue webhook deliveries with automatic retries
- Track delivery status and history
- Secure payload signing using HMAC-SHA256
- Exponential backoff for failed deliveries
- Containerized deployment with Docker
- Horizontally scalable architecture

## System Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  FastAPI    │────▶│  PostgreSQL │
└─────────────┘     │   Server    │     └─────────────┘
                    └─────────────┘
                          │
                          ▼
                    ┌─────────────┐     ┌─────────────┐
                    │    Redis    │────▶│   Workers   │
                    └─────────────┘     └─────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │ Target Webhooks │
                                    └─────────────────┘
```

## Installation & Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ (if running without Docker)
- Redis 7+ (if running without Docker)

### Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd webhook-service
   ```

2. Create environment files:
   ```bash
   # .env
   DATABASE_URL=postgresql://webhook:secret@db:5432/webhook_db
   REDIS_URL=redis://redis:6379/0
   ```

3. Start the services:
   ```bash
   docker-compose up --build
   ```

The service will be available at `http://localhost:8000`.

### Manual Setup (Development)

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   .\venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL and Redis locally

4. Run migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the services:
   ```bash
   # Terminal 1: API Server
   uvicorn api.main:app --reload

   # Terminal 2: Worker
   python worker/worker.py
   ```

## API Documentation

### Create a Subscription

```http
POST /subscriptions
Content-Type: application/json

{
    "target_url": "https://your-webhook-endpoint.com/webhook",
    "secret": "your-signing-secret"  // Optional
}
```

Response:
```json
{
    "id": 1,
    "target_url": "https://your-webhook-endpoint.com/webhook",
    "secret": "your-signing-secret",
    "created_at": "2025-05-09T18:31:09.127696+00:00"
}
```

### Enqueue a Delivery

```http
POST /deliveries
Content-Type: application/json

{
    "subscription_id": 1,
    "payload": "{\"event\":\"user.created\",\"data\":{\"id\":123}}"
}
```

Response:
```json
{
    "id": 1,
    "subscription_id": 1,
    "payload": "{\"event\":\"user.created\",\"data\":{\"id\":123}}",
    "status": "pending",
    "attempts": 0,
    "last_error": null
}
```

### List Deliveries for a Subscription

```http
GET /deliveries/subscription/{subscription_id}
```

Response:
```json
{
    "deliveries": [
        {
            "id": 1,
            "subscription_id": 1,
            "payload": "...",
            "status": "success",
            "attempts": 1,
            "last_error": null
        }
    ]
}
```

## Integrating with Your Application

### As a Docker Service

1. Add to your `docker-compose.yml`:
   ```yaml
   webhook-service:
     image: your-registry/webhook-service:latest
     environment:
       - DATABASE_URL=postgresql://webhook:secret@db:5432/webhook_db
       - REDIS_URL=redis://redis:6379/0
     ports:
       - "8000:8000"
   ```

2. Create a subscription:
   ```python
   import requests

   response = requests.post(
       "http://webhook-service:8000/subscriptions",
       json={
           "target_url": "https://your-service/webhook",
           "secret": "your-secret"
       }
   )
   subscription_id = response.json()["id"]
   ```

3. Send webhook deliveries:
   ```python
   requests.post(
       "http://webhook-service:8000/deliveries",
       json={
           "subscription_id": subscription_id,
           "payload": json.dumps({"event": "user.created", "data": {...}})
       }
   )
   ```

### Receiving Webhooks

1. Set up an endpoint in your application:
   ```python
   from fastapi import FastAPI, Request, HTTPException
   import hmac
   import hashlib

   app = FastAPI()

   @app.post("/webhook")
   async def webhook(request: Request):
       # Verify signature if using signing
       signature = request.headers.get("X-Signature")
       payload = await request.body()
       expected_sig = hmac.new(
           "your-secret".encode(),
           payload,
           hashlib.sha256
       ).hexdigest()
       
       if signature != expected_sig:
           raise HTTPException(status_code=401)
           
       # Process webhook
       data = await request.json()
       # Handle webhook payload
       return {"status": "processed"}
   ```

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `MAX_RETRIES` (optional): Maximum delivery attempts (default: 5)
- `INITIAL_BACKOFF` (optional): Initial retry delay in seconds (default: 2)

### Scaling

The service is designed to scale horizontally:

1. **API Servers**: Add more FastAPI containers behind a load balancer
2. **Workers**: Scale the worker containers to process more deliveries
3. **Database**: Use PostgreSQL replication for read scaling
4. **Redis**: Set up Redis Sentinel or Cluster for high availability

## Monitoring & Maintenance

### Health Checks

Monitor these endpoints:
- `/health`: API server health
- Database connection status
- Redis connection status
- Worker process status

### Metrics to Track

- Webhook delivery success rate
- Average delivery time
- Retry counts
- Queue length
- Error rates by endpoint

### Logging

The service logs important events:
- Delivery attempts
- Subscription creation
- System errors
- Worker status

## Security Considerations

1. **Payload Signing**: Use webhook secrets for all production webhooks
2. **TLS**: Always use HTTPS for webhook endpoints
3. **Rate Limiting**: Implement rate limiting for subscription creation
4. **Access Control**: Add authentication for managing subscriptions
5. **Payload Validation**: Validate payload size and content

## Best Practices

1. **Idempotency**: Ensure webhook handlers are idempotent
2. **Timeouts**: Set appropriate timeout values for webhook delivery
3. **Monitoring**: Set up alerts for failed deliveries
4. **Backup**: Regular database backups
5. **Documentation**: Keep API documentation updated

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file for details