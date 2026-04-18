from redis_db import QUEUE_NAME , redis_connection
import json

id = 0
def enqueue(func_name, **kwargs):
    global id
    task = {
        "id": str(id),
        "func": func_name,
        "args": kwargs,
        "retries": 0,
        "max_retries": 3
    }
    id+=1
    
    redis_connection.lpush(QUEUE_NAME, json.dumps(task))

