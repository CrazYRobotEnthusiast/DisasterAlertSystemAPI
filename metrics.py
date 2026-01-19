from prometheus_client import Counter, Gauge, Summary, Histogram

# A, H, I: Alerts, Success Rate, and Regional Distribution
ALERTS_DISPATCHED = Counter(
    'disaster_alerts_total', 
    'Total alerts sent', 
    ['region', 'status']
)

# B: Login Pie Chart
LOGIN_ATTEMPTS = Counter(
    'disaster_login_attempts_total', 
    'Total login attempts', 
    ['status']
)

# C: Current Logins
ACTIVE_ADMINS = Gauge(
    'disaster_active_admins', 
    'Current number of logged-in admin sessions'
)

# D: Alert Latency (API Request to Completion)
ALERT_LATENCY = Summary(
    'disaster_alert_request_latency_seconds', 
    'Time spent processing the alert request (End-to-End)'
)

# E: Queue Depth
QUEUE_DEPTH = Gauge(
    'disaster_queue_depth', 
    'Number of tasks waiting in the buffer'
)

# F: Worker Processing Time
WORKER_TIME = Summary(
    'disaster_worker_processing_seconds', 
    'Time the worker spent sending a batch'
)

# G: Thread Utilisation
ACTIVE_WORKER_THREADS = Gauge(
    'disaster_active_worker_threads', 
    'Number of active threads currently sending messages'
)