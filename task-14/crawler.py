import asyncio
import aiohttp
import urllib.parse
import urllib.robotparser
from bs4 import BeautifulSoup
import argparse
import time
import json
import os
import xml.etree.ElementTree as ET
from collections import defaultdict

class AsyncCrawler:
    def __init__(self, seed_url, max_depth, concurrency):
        self.seed_url = seed_url
        self.base_domain = urllib.parse.urlparse(seed_url).netloc
        self.scheme = urllib.parse.urlparse(seed_url).scheme
        self.max_depth = max_depth
        self.concurrency = concurrency
        
        self.queue = asyncio.Queue()
        self.visited = set()
        self.queued = set()
        
        self.graph = defaultdict(lambda: {'status': None, 'redirects': [], 'outbound': set()})
        self.inbound_links = defaultdict(set)
        
        self.robot_parsers = {}
        self.skipped_robots = 0
        self.duplicates_avoided = 0
        self.start_time = 0
        
        self.known_sitemap_urls = set()

    async def get_robot_parser(self, session, url):
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc
        scheme = parsed.scheme
        if domain not in self.robot_parsers:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = f"{scheme}://{domain}/robots.txt"
            try:
                async with session.get(robots_url, timeout=5) as resp:
                    if resp.status == 200:
                        content = await resp.text()
                        rp.parse(content.splitlines())
                    else:
                        rp.allow_all = True
            except Exception:
                rp.allow_all = True
            
            rp.set_url(robots_url)
            self.robot_parsers[domain] = rp
        
        return self.robot_parsers[domain]

    def is_allowed(self, rp, url):
        if getattr(rp, 'allow_all', False):
            return True
        return rp.can_fetch("*", url)

    def normalize_url(self, base, link):
        joined = urllib.parse.urljoin(base, link)
        parsed = urllib.parse.urlparse(joined)
        clean_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, ''))
        return clean_url

    async def fetch_sitemap(self, session):
        sitemap_url = f"{self.scheme}://{self.base_domain}/sitemap.xml"
        try:
            async with session.get(sitemap_url, timeout=5) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    try:
                        root = ET.fromstring(text)
                        for loc in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                            if loc.text:
                                self.known_sitemap_urls.add(self.normalize_url(sitemap_url, loc.text))
                    except ET.ParseError:
                        pass
        except Exception:
            pass

    async def worker(self, session):
        while True:
            try:
                url, depth = await self.queue.get()
                await self.process_url(session, url, depth)
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[ERROR] Worker exception: {e}")
                self.queue.task_done()

    async def process_url(self, session, url, depth):
        if depth > self.max_depth:
            return

        rp = await self.get_robot_parser(session, url)
        if not self.is_allowed(rp, url):
            self.skipped_robots += 1
            return

        self.visited.add(url)
        start_t = time.time()
        
        try:
            async with session.get(url, allow_redirects=True, timeout=10) as resp:
                elapsed = time.time() - start_t
                final_url = str(resp.url)
                
                redirects = []
                if resp.history:
                    for h in resp.history:
                        redirects.append(str(h.url))
                    
                self.graph[url]['status'] = resp.history[0].status if resp.history else resp.status
                self.graph[url]['redirects'] = redirects
                if final_url != url:
                    self.graph[url]['redirect_dest'] = final_url
                
                if final_url != url:
                    self.visited.add(final_url)
                    self.graph[final_url]['status'] = resp.status
                    print(f"[DEPTH {depth}] {url:<40} {self.graph[url]['status']} -> {urllib.parse.urlparse(final_url).path}")
                else:
                    status_text = "OK" if resp.status == 200 else ("NOT FOUND" if resp.status == 404 else resp.status)
                    print(f"[DEPTH {depth}] {url:<40} {resp.status} {status_text:<10} {elapsed:.2f}s")

                if resp.status == 200 and 'text/html' in resp.headers.get('Content-Type', ''):
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if href.startswith('mailto:') or href.startswith('tel:') or href.startswith('javascript:'):
                            continue
                            
                        next_url = self.normalize_url(final_url, href)
                        parsed_next = urllib.parse.urlparse(next_url)
                        
                        if parsed_next.netloc == self.base_domain:
                            self.graph[final_url]['outbound'].add(next_url)
                            self.inbound_links[next_url].add(final_url)
                            
                            if next_url not in self.visited and next_url not in self.queued:
                                if depth < self.max_depth:
                                    self.queued.add(next_url)
                                    self.queue.put_nowait((next_url, depth + 1))
                            elif next_url in self.visited or next_url in self.queued:
                                self.duplicates_avoided += 1

        except Exception as e:
            self.graph[url]['status'] = 0
            print(f"[DEPTH {depth}] {url:<40} ERR: {e}")

    async def crawl(self):
        print("=== Crawl Started ===")
        print(f"[INFO] Seed: {self.seed_url}")
        print(f"[INFO] Max depth: {self.max_depth} | Concurrency: {self.concurrency} | Respecting robots.txt: YES\n")
        
        self.start_time = time.time()
        self.queued.add(self.seed_url)
        self.queue.put_nowait((self.seed_url, 0))
        
        async with aiohttp.ClientSession() as session:
            await self.fetch_sitemap(session)
            
            workers = [asyncio.create_task(self.worker(session)) for _ in range(self.concurrency)]
            await self.queue.join()
            
            for w in workers:
                w.cancel()
                
        elapsed = time.time() - self.start_time
        print(f"\n=== Crawl Complete ({elapsed:.1f}s) ===")
        print(f"Pages crawled:      {len(self.visited)}")
        print(f"Unique URLs found:  {len(self.graph)}")
        print(f"Skipped (robots):   {self.skipped_robots}")
        print(f"Duplicates avoided: {self.duplicates_avoided}\n")
        
        self.generate_report()
        self.export_data()

    def generate_report(self):
        print("=== SEO Audit Report ===")
        
        broken = []
        for url, data in self.graph.items():
            if data['status'] == 404:
                inbounds = list(self.inbound_links[url])
                paths = [urllib.parse.urlparse(i).path for i in inbounds[:3]]
                linked_from = ", ".join(paths)
                broken.append(f"  - {urllib.parse.urlparse(url).path} (linked from: {linked_from})")
                
        print("Broken Links (404):")
        if broken:
            for b in broken:
                print(b)
        else:
            print("  None")
            
        print("\nRedirect Chains (301/302):")
        redirects = []
        for url, data in self.graph.items():
            if data['redirects']:
                chain_paths = [urllib.parse.urlparse(u).path for u in data['redirects']]
                final_path = urllib.parse.urlparse(data['redirect_dest']).path
                hops = len(data['redirects'])
                hop_str = f"{hops} hop{'s' if hops > 1 else ''}"
                if hops > 1:
                    hop_str += " — consider fixing"
                
                chain_str = " -> ".join(chain_paths) + f" -> {final_path}"
                redirects.append(f"  - {chain_str} ({hop_str})")
                
        if redirects:
            for r in redirects:
                print(r)
        else:
            print("  None")

        print("\nOrphan Pages (no inbound links):")
        orphans = []
        for url in self.known_sitemap_urls:
            if not self.inbound_links[url] and url != self.seed_url:
                orphans.append(f"  - {urllib.parse.urlparse(url).path}")
                
        if orphans:
            for o in orphans:
                print(o)
        else:
            print("  None")
        print()

    def export_data(self):
        os.makedirs("output", exist_ok=True)
        
        serializable_graph = {}
        for k, v in self.graph.items():
            serializable_graph[k] = {
                'status': v['status'],
                'redirects': v['redirects'],
                'outbound': list(v['outbound'])
            }
            if 'redirect_dest' in v:
                serializable_graph[k]['redirect_dest'] = v['redirect_dest']
                
        with open("output/crawl_graph.json", "w") as f:
            json.dump(serializable_graph, f, indent=2)
            
        urlset = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        for url, data in self.graph.items():
            if data['status'] == 200:
                url_el = ET.SubElement(urlset, 'url')
                loc = ET.SubElement(url_el, 'loc')
                loc.text = url
                
        tree = ET.ElementTree(urlset)
        tree.write("output/sitemap.xml", encoding='utf-8', xml_declaration=True)
        
        print("Crawl graph saved to: output/crawl_graph.json")
        print("Site map saved to:    output/sitemap.xml")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concurrent Web Crawler")
    parser.add_argument('--seed', type=str, required=True, help="Seed URL")
    parser.add_argument('--depth', type=int, default=3, help="Max depth")
    parser.add_argument('--concurrency', type=int, default=20, help="Concurrency limit")
    args = parser.parse_args()
    
    crawler = AsyncCrawler(args.seed, args.depth, args.concurrency)
    asyncio.run(crawler.crawl())
