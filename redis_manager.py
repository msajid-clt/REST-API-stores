import redis


import redis
# Setup our redis connection for storing the blocklisted tokens. You will probably
# want your redis instance configured to persist data to disk, so that a restart
# does not cause your application to forget that a JWT was revoked.
class RedisManager():
    def __init__(self):
        # Connect to redis etc
        self.jwt_redis_blocklist = redis.StrictRedis(
                host="localhost", port=6379, db=0, decode_responses=True
        )

redis_manager = RedisManager()