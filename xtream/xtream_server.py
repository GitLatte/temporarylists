import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

CREDENTIALS = {
    'sinetech': 'sinetech'  # username: password
}

class XtreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        # Get username and password from query parameters
        username = query_params.get('username', [''])[0]
        password = query_params.get('password', [''])[0]
        
        # Validate credentials
        if username not in CREDENTIALS or CREDENTIALS[username] != password:
            self.send_response(401)
            self.end_headers()
            return
        
        # Get the m3u file path from the URL path
        file_path = parsed_path.path.strip('/')
        if not file_path.endswith('.m3u'):
            file_path += '.m3u'
            
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        
        # Check if file exists
        if not os.path.exists(full_path):
            self.send_response(404)
            self.end_headers()
            return
            
        # Read and serve the m3u file
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/x-mpegurl')
            self.end_headers()
            self.wfile.write(content.encode())
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()

def run(port=80):
    server_address = ('', port)
    httpd = HTTPServer(server_address, XtreamHandler)
    print(f'Starting Xtream server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()