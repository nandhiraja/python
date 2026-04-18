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
    print(f"Task Queued : {task['id']} ({func_name})")

if __name__ == "__main__":
    from multiprocessing import Process
    import time
    from worker import worker

    for i in range(3):
        Process(target=worker, args=(i+1,)).start()

    time.sleep(2)

    enqueue("add", a=5, b=10)
    enqueue("generate_thumbnail", image_id=4521, size=(256, 256))
    enqueue("send_email", to="bob@co.com", template="welcome")
