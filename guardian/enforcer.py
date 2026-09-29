"""
DataGuard - Guardian Enforcer (Core Project)
The middleware that intercepts all requests and enforces policies.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json, yaml, datetime, threading
from urllib.request import urlopen, Request
from urllib.error import URLError

# ─── Load Policies ───────────────────────────────────────────────
with open("policies.yaml") as f:
    config = yaml.safe_load(f)

POLICIES = config["policies"]
LOG = []          # in-memory audit log
STATS = {"total": 0, "allowed": 0, "denied": 0, "violations": 0}

def check_policy(subject, target, operation):
    
    for rule in POLICIES:
        if rule["subject"] == subject and rule["target"] == target:
            if operation.upper() in [op.upper() for op in rule["operations"]]:
                return rule["action"]
    return "DENY"   # default deny — safest option

def add_log(subject, target, operation, result, violation=False):
    """Write to audit log"""
    entry = {
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "subject": subject,
        "target": target,
        "operation": operation,
        "result": result,
        "violation": violation
    }
    LOG.insert(0, entry)
    if len(LOG) > 50:
        LOG.pop()
    STATS["total"] += 1
    if result == "ALLOW":
        STATS["allowed"] += 1
    else:
        STATS["denied"] += 1
        if violation:
            STATS["violations"] += 1
    print(f"[{entry['time']}] {result:6} | {subject} → {target} [{operation}]{'  ⚠️  VIOLATION!' if violation else ''}")

# ─── HTTP Handler ─────────────────────────────────────────────────
class GuardianHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # suppress default logs

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Service, X-Target, X-Operation")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        # Dashboard API endpoints
        if self.path == "/logs":
            self._json({"logs": LOG, "stats": STATS})
        elif self.path == "/policies":
            self._json({"policies": POLICIES})
        elif self.path == "/health":
            self._json({"status": "Guardian is running", "version": "1.0"})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/check":
            # Read request body
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))

            subject   = body.get("subject", "unknown")
            target    = body.get("target", "unknown")
            operation = body.get("operation", "READ")

            # ── THE CORE DECISION ──
            result = check_policy(subject, target, operation)
            violation = (result == "DENY")
            add_log(subject, target, operation, result, violation)

            status = 200 if result == "ALLOW" else 403
            self.send_response(status)
            self.send_cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "result": result,
                "subject": subject,
                "target": target,
                "operation": operation,
                "message": f"✅ Access ALLOWED" if result == "ALLOW" else f"🚫 Access BLOCKED by DataGuard policy"
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def _json(self, data):
        self.send_response(200)
        self.send_cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

# ─── Start Server ─────────────────────────────────────────────────
if __name__ == "__main__":
    PORT = 8080
    server = HTTPServer(("0.0.0.0", PORT), GuardianHandler)
    print("=" * 50)
    print("  🛡️  DataGuard Guardian Enforcer")
    print(f"  Running on http://localhost:{PORT}")
    print(f"  Policies loaded: {len(POLICIES)} rules")
    print("=" * 50)
    server.serve_forever()
