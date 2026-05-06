from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/robots.txt':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"User-agent: *\nDisallow: /private\n")
            return
            
        if self.path == '/sitemap.xml':
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            xml = """<?xml version="1.0" encoding="UTF-8"?>
            <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
               <url><loc>http://localhost:8080/</loc></url>
               <url><loc>http://localhost:8080/about</loc></url>
               <url><loc>http://localhost:8080/products</loc></url>
               <url><loc>http://localhost:8080/orphan-page</loc></url>
            </urlset>"""
            self.wfile.write(xml.encode())
            return

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html><body>
                <a href="/about">About</a>
                <a href="/products">Products</a>
                <a href="/old-promo">Old Promo</a>
                <a href="/private">Private</a>
                <a href="/broken">Broken</a>
                </body></html>
            """)
            return

        if self.path == '/about':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><a href="/">Home</a><a href="/broken">Broken</a></body></html>')
            return

        if self.path == '/products':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><a href="/">Home</a></body></html>')
            return
            
        if self.path == '/old-promo':
            self.send_response(301)
            self.send_header('Location', '/products')
            self.end_headers()
            return
            
        if self.path == '/orphan-page':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body>I am an orphan</body></html>')
            return
            
        if self.path == '/private':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body>Top secret</body></html>')
            return

        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Not found')

def run(server_class=HTTPServer, handler_class=DummyServer, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
