import http.server
import socketserver
import threading
import logging

class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        # Override to use the logging module instead of printing to stderr
        logging.info("%s - - [%s] %s" %
                     (self.client_address[0],
                      self.log_date_time_string(),
                      format % args))

def start_health_server(port=8080):
    handler = HealthCheckHandler
    httpd = socketserver.TCPServer(("0.0.0.0", port), handler)
    
    logging.info(f"Health check server started on port {port}")
    
    # Run the server in a separate thread so it doesn't block the main application
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True  # Set as daemon so it will be killed when the main program exits
    server_thread.start()
    
    return httpd

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start the health check server
    httpd = start_health_server()
    
    try:
        # Keep the main thread alive
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logging.info("Stopping health check server...")
        httpd.shutdown()