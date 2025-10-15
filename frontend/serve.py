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

PORT = 8080

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def start_server():
    # Change to the frontend directory
    frontend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(frontend_dir)
    
    try:
        with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
            print(f"TEX-SARTHI Frontend Server")
            print(f"Serving at: http://localhost:{PORT}")
            print(f"Serving files from: {frontend_dir}")
            print(f"Make sure the backend is running on port 3000")
            print("=" * 50)
            print("Press Ctrl+C to stop the server")
            
            # Auto-open browser after a short delay
            import threading
            def open_browser():
                import time
                time.sleep(2)
                webbrowser.open(f'http://localhost:{PORT}')
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 10048:  # Port already in use
            print(f"Port {PORT} is already in use. Trying port {PORT + 1}")
            PORT = PORT + 1
            start_server()
        else:
            print(f"Error starting server: {e}")
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    start_server()