from task import FUNCTIONS

def process_task(task):
    func_name = task["func"]
    args = task["args"]

    func = FUNCTIONS.get(func_name)


    if not func:
        raise Exception("Function not found...")

    return func(**args)