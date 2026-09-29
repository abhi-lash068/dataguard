"""
DataGuard - Health Records Service
Simulates a health records microservice.
Allowed to access patient-db, blocked from payments-db.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.request import urlopen, Request
from urllib.error import URLError

GUARDIAN_URL = "http://localhost:8080/check"
SERVICE_NAME = "health-service"

def ask_guardian(target, operation="READ"):
    payload = json.dumps({
        "subject": SERVICE_NAME,
        "target": target,
        "operation": operation
    }).encode()
    try:
        req = Request(GUARDIAN_URL, data=payload,
                      headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=3) as resp:
            return json.loads(resp.read()), resp.status
    except URLError as e:
        if hasattr(e, 'code') and e.code == 403:
            return json.loads(e.read()), 403
        return {"result": "ERROR", "message": str(e)}, 500

class HealthHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        # Allowed — health service reads its own patient DB
        if self.path == "/read-patients":
            resp, status = ask_guardian("patient-db", "READ")
            self._reply(resp, status)

        # Allowed — health service writes patient DB
        elif self.path == "/write-patients":
            resp, status = ask_guardian("patient-db", "WRITE")
            self._reply(resp, status)

        # BLOCKED — health service tries to read payments DB
        elif self.path == "/read-payments":
            resp, status = ask_guardian("payments-db", "READ")
            self._reply(resp, status)

        else:
            self._reply({"service": SERVICE_NAME, "status": "running",
                         "endpoints": ["/read-patients", "/write-patients", "/read-payments"]}, 200)

    def _reply(self, data, status=200):
        self.send_response(status)
        self.send_cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

if __name__ == "__main__":
    PORT = 5002
    print(f"🏥 Health Service running on http://localhost:{PORT}")
    HTTPServer(("0.0.0.0", PORT), HealthHandler).serve_forever()
