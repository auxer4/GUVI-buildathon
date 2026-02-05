from app.storage.redis_client import get_redis_client

r = get_redis_client()
print("PING:", r.ping())
