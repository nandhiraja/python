import redis
print("Initial: Trying to connect redis...")
redis_connection =  redis.Redis(host='localhost', port=6379, decode_responses=True)
print("Initial: Connection successfull..")


QUEUE_NAME = "task_queue"
DEAD_TASK_NAME = "dead_task_queue" 
