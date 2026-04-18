## Distributed Task Queue

**Description:** Implement a producer-consumer task queue that distributes work across multiple worker processes. Include task serialization, retry logic with exponential backoff, dead-letter queues, and result backends.

**Prerequisites:**

- `multiprocessing` and `threading` modules
- `pickle` and `json` serialization
- Redis (via `redis-py`) as a message broker
- Socket programming basics
- Exponential backoff algorithm
- Producer-consumer and pub/sub patterns


```
          Producer
              ↓
        Redis Queue
        ↓    ↓    ↓
     Worker Worker Worker
     
```