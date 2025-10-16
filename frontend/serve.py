#!/usr/bin/env python3
"""
Simple HTTP server to serve the TEX-SARTHI frontend
This allows the frontend to access the backend API via CORS
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

PORT = 8080
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:3000')

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        # Disable caching so frontend changes (like api.js) are always picked up
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def _proxy_to_backend(self, method: str):
        # Only proxy /api and /api/* to backend, avoid matching /api.js
        if not (self.path == '/api' or self.path.startswith('/api/')):
            return False
        target_url = f"{BACKEND_URL}{self.path}"
        try:
            # Read request body if present
            data = None
            length = int(self.headers.get('Content-Length', 0) or 0)
            if length > 0:
                data = self.rfile.read(length)

            # Prepare proxied request
            req = urllib.request.Request(target_url, data=data, method=method)
            # Forward important headers
            for header in ['Content-Type', 'Authorization']:
                if header in self.headers:
                    req.add_header(header, self.headers[header])

            with urllib.request.urlopen(req) as resp:
                body = resp.read()
                self.send_response(resp.status)
                # Forward content-type; fall back to json
                self.send_header('Content-Type', resp.headers.get('Content-Type', 'application/json'))
                self.end_headers()
                if body:
                    self.wfile.write(body)
            return True
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', e.headers.get('Content-Type', 'application/json'))
            self.end_headers()
            err_body = e.read()
            if err_body:
                self.wfile.write(err_body)
            return True
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(f"{{\"error\": \"Proxy error: {str(e)}\"}}".encode('utf-8'))
            return True

    def do_GET(self):
        # Explicitly serve api.js if requested (resolve relative to this file regardless of cwd)
        if self.path == '/api.js':
            try:
                import os
                base_dir = os.path.dirname(__file__)
                api_js_path = os.path.join(base_dir, 'api.js')
                with open(api_js_path, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/javascript')
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception:
                # Fall through to default handler
                pass
        if self._proxy_to_backend('GET'):
            return
        return super().do_GET()

    def do_POST(self):
        if self._proxy_to_backend('POST'):
            return
        return super().do_POST()

    def do_PUT(self):
        if self._proxy_to_backend('PUT'):
            return
        return super().do_PUT()

    def do_DELETE(self):
        if self._proxy_to_backend('DELETE'):
            return
        return super().do_DELETE()

def start_server(port: int = PORT):
    # Change to the frontend directory
    frontend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(frontend_dir)
    
    try:
        with socketserver.TCPServer(("", port), CORSRequestHandler) as httpd:
            print(f"TEX-SARTHI Frontend Server")
            print(f"Serving at: http://localhost:{port}")
            print(f"Serving files from: {frontend_dir}")
            print(f"Make sure the backend is running on port 3000")
            print("=" * 50)
            print("Press Ctrl+C to stop the server")
            
            # Auto-open browser after a short delay
            import threading
            def open_browser():
                import time
                time.sleep(2)
                webbrowser.open(f'http://localhost:{port}')
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 10048:  # Port already in use
            next_port = port + 1
            print(f"Port {port} is already in use. Trying port {next_port}")
            start_server(next_port)
        else:
            print(f"Error starting server: {e}")
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    start_server()