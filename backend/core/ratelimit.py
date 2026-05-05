import time
from backend.db.redis_client import get_redis

async def check_rate_limit(client_id: str, capacity: int = 10000, fill_rate: float = 10000.0) -> bool:
    """
    Token bucket rate limiting using Redis.
    """
    redis = await get_redis()
    key = f"rate_limit:{client_id}"
    now = time.time()
    
    script = """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local fill_rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    
    local bucket = redis.call('HMGET', key, 'tokens', 'last_update')
    local tokens = tonumber(bucket[1])
    local last_update = tonumber(bucket[2])
    
    if not tokens then
        tokens = capacity
        last_update = now
    else
        local delta = now - last_update
        tokens = math.min(capacity, tokens + delta * fill_rate)
    end
    
    if tokens >= 1 then
        redis.call('HMSET', key, 'tokens', tokens - 1, 'last_update', now)
        redis.call('EXPIRE', key, math.ceil(capacity / fill_rate) * 2)
        return 1
    else
        redis.call('HMSET', key, 'tokens', tokens, 'last_update', now)
        return 0
    end
    """
    result = await redis.eval(script, 1, key, capacity, fill_rate, now)
    return bool(result)
