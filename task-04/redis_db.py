import redis

redis_connection =  redis.Redis(host='localhost', port=6379)

QUEUE_NAME = "task_queue"
DEAD_TASK_NAME = "dead_task_queue" 
