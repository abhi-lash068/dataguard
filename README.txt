===============================================
  DataGuard — Prototype Setup & Run Guide
===============================================

REQUIREMENTS:
  - Python 3.x (already installed ✅)
  - PyYAML library

STEP 1 — Install PyYAML (one time only):
  pip install pyyaml

STEP 2 — Open 3 terminals:

  Terminal 1 (Guardian — run this FIRST):
  ----------------------------------------
  cd dataguard/guardian
  python enforcer.py

  Terminal 2 (Payment Service):
  ----------------------------------------
  cd dataguard
  python payment_service.py

  Terminal 3 (Health Service):
  ----------------------------------------
  cd dataguard
  python health_service.py

STEP 3 — Open Dashboard:
  Open dashboard/index.html in Chrome browser
  (just double-click the file)

STEP 4 — Demo 
  Click "Payment attacks Patient DB" → BLOCKED 🚫
  Click "Health reads Patient DB"    → ALLOWED ✅
  Click "Auto Demo"                  → full sequence!

===============================================
  URLs:
  Guardian API  → http://localhost:8080
  Payment Svc   → http://localhost:5001
  Health Svc    → http://localhost:5002
  Dashboard     → open index.html in browser
===============================================
