from flask import Flask, request, jsonify, session, Response
import threading
import time
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from metrics import LOGIN_ATTEMPTS, ACTIVE_ADMINS, ALERT_LATENCY

# Import your SOLID classes
from infrastructure import SQLiteDB, TwilioMessageSender, InMemoryTaskQueue, SQLiteAuthenticator
from domain import (
    PhoneNumberFetcher, 
    RegionContactService, 
    AsyncAlertDispatcher, 
    AlertWorker,
    AlertController
)

app = Flask(__name__)
app.secret_key = "super_secret_safety_key"

# ==========================================
# 1. SYSTEM INITIALIZATION (Composition Root)
# ==========================================
db = SQLiteDB()
auth = SQLiteAuthenticator()
queue = InMemoryTaskQueue()
sender = TwilioMessageSender()

# Wiring the Domain logic
fetcher = PhoneNumberFetcher(db)
service = RegionContactService(fetcher)
dispatcher = AsyncAlertDispatcher(queue)

# Worker with 10 parallel threads for message sending
worker = AlertWorker(sender, max_workers=10)
controller = AlertController(service, dispatcher)

# ==========================================
# 2. BACKGROUND WORKER DEFINITION
# ==========================================
# We define the function FIRST so it exists when the thread starts
def start_worker_loop(w, q):
    """Continuously processes the queue in the background."""
    print("[SYSTEM] Background AlertWorker loop started.")
    while True:
        if not q.is_empty():
            w.process_next(q)
        else:
            time.sleep(1) # Sleep to save CPU when queue is empty

# Now we can safely start the thread
threading.Thread(target=start_worker_loop, args=(worker, queue), daemon=True).start()

# ==========================================
# 3. API ROUTES (Protected by Authentication)
# ==========================================
@app.route('/metrics')
def metrics():
    """Exposes metrics for Prometheus scraping."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if auth.authenticate(data['username'], data['password']):
        session['logged_in'] = True
        ACTIVE_ADMINS.inc() # Requirement C
        LOGIN_ATTEMPTS.labels(status='success').inc() # Requirement B
        return jsonify({"status": "Success"}), 200
    
    LOGIN_ATTEMPTS.labels(status='failure').inc() # Requirement B
    return jsonify({"status": "Error"}), 401

@app.route('/logout')
def logout():
    if session.get('logged_in'):
        ACTIVE_ADMINS.dec() # Requirement C
        session.clear()
    return jsonify({"status": "Logged out"})

@app.route('/send_alert', methods=['POST'])
@ALERT_LATENCY.time()
def send_alert():
    """
    Protected Endpoint: Triggers the Disaster Alert.
    Requires 'logged_in' session.
    """
    # Authorization Check
    if not session.get('logged_in'):
        return jsonify({"status": "Error", "message": "Unauthorized. Please login first."}), 403

    try:
        data = request.get_json()
        if not data or 'message' not in data or 'regions' not in data:
            return jsonify({"status": "Error", "message": "Invalid input"}), 400

        # Trigger the SOLID Controller logic
        controller.trigger_disaster_alert(data['message'], data['regions'])

        # Wait until the background queue is empty (Requirement)
        while not queue.is_empty():
            time.sleep(0.2)

        return jsonify({
            "status": "Success",
            "message": "all alerts sent"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "Error", 
            "message": str(e)
        }), 500



if __name__ == '__main__':
    # Initialize the system
    app.run(debug=True, port=5000)