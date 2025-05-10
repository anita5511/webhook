import os
from redis import Redis
from rq import Queue

REDIS_URL = os.getenv("REDIS_URL")
redis_conn = Redis.from_url(REDIS_URL)
queue = Queue('deliveries', connection=redis_conn, default_timeout=300)