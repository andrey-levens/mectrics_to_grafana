from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import json
import threading
import time

def check_service_status(service_name):
    try:
        status = subprocess.run(
            ["systemctl", "status", service_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        if "active (running)" in status.stdout:
            return 1
        elif "inactive" in status.stdout:
            return 0
        else:
            return 0
    except Exception:
        return 0

class StatusHandler(BaseHTTPRequestHandler):
    nginx_status = 0
    apache_status = 0

    def do_GET(self):
        response = {
            "nginx_status": self.nginx_status,
            "apache_status": self.apache_status
        }
        
        json_response = json.dumps(response)
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json_response.encode("utf-8"))

def update_status():
    while True:
        StatusHandler.nginx_status = check_service_status("nginx")
        StatusHandler.apache_status = check_service_status("apache2")
        time.sleep(20)

def run_server(server_class=HTTPServer, handler_class=StatusHandler, port=8087):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print("Starting server on port {}...".format(port))
    httpd.serve_forever()

if __name__ == "__main__":
    status_thread = threading.Thread(target=update_status)
    status_thread.daemon = True
    status_thread.start()
    run_server()
