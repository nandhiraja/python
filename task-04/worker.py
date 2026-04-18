from task import FUNCTIONS
from redis_db import redis_connection,DEAD_TASK_NAME,QUEUE_NAME
import time
import json
def process_task(task):
    func_name = task["func"]
    args = task["args"]

    func = FUNCTIONS.get(func_name)


    if not func:
        raise Exception("Function not found...")

    return func(**args)

def worker(worker_id):

    print(f"[WORKER-{worker_id}] Started")

    while True:
        task_data = redis_connection.rpop(QUEUE_NAME)

        if not task_data:
            time.sleep(1)
            continue

        task = json.loads(task_data)
        task_id = task["id"]
        print(f"[WORKER-{worker_id}] Picked task {task_id} ({task['func']})")


        start_time = time.time()

        try:
            result = process_task(task)
            duration = round(time.time() - start_time, 2)

            print(f"[WORKER-{worker_id}] SUCCESS {task_id} in {duration} >>{result}")

        except Exception as e:
            task["retries"] += 1

            if task["retries"] <= task["max_retries"]:
                delay = 2 ** task["retries"]
                print(f"[WORKER-{worker_id}] FAILED {task_id} ({e}) >> retry {task['retries']} in {delay}s")

                time.sleep(delay)
                redis_connection.lpush(QUEUE_NAME, json.dumps(task))

            else:
                print(f"[WORKER-{worker_id}] FAILED {task_id} ({e}) >> retry {task['retries']} in {delay}s")

                redis_connection.lpush(DEAD_TASK_NAME, json.dumps(task))