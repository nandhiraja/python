## Concurrent Web Crawler with Depth Control

**Description:** Build a web crawler that starts from a seed URL, extracts links, and recursively crawls up to a configurable depth with concurrency, deduplication, and `robots.txt` compliance.

**Prerequisites:**

- `asyncio` and `aiohttp` for async HTTP requests
- BFS graph traversal algorithm
- `urllib.parse` for URL normalization and joining
- `robotparser` for `robots.txt` compliance
- Sets and queues for deduplication
- `json` for crawl graph export

