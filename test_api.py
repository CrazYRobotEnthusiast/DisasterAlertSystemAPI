import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def run_comprehensive_test():
    session = requests.Session()

    print("\n--- [1] Generating Login Metrics (B & C) ---")
    # 2 Failed logins to show failure slice in Pie Chart
    for _ in range(2):
        session.post(f"{BASE_URL}/login", json={"username": "admin", "password": "wrong_password"})
    
    # 1 Successful login
    session.post(f"{BASE_URL}/login", json={"username": "admin", "password": "password123"})
    print("Login sequence complete.")

    print("\n--- [2] Generating Regional & Success Rate Metrics (H & I) ---")
    # We will trigger alerts for different regions to see the distribution
    test_scenarios = [
        {"msg": "Flood in Delhi", "regs": ["Delhi"]},      # Has 1 Valid, 1 Invalid
        {"msg": "Fire in Mumbai", "regs": ["Mumbai"]},     # Has 1 Valid
        {"msg": "Storm in Kolkata", "regs": ["Kolkata"]},  # Has 1 Invalid
        {"msg": "Heatwave in Chennai", "regs": ["Chennai"]} # Has 1 Valid
    ]

    for scenario in test_scenarios:
        print(f"Sending alert to {scenario['regs']}...")
        resp = session.post(f"{BASE_URL}/send_alert", json={
            "message": scenario['msg'],
            "regions": scenario['regs']
        })
        print(f"Response: {resp.json()}")

    print("\n--- [3] Generating High-Traffic Metrics (A, D, E, F, G) ---")
    print("Simulating a rapid burst of alerts to observe Queue Depth and Thread Utilisation...")
    
    # Rapid fire requests to build up the queue
    for i in range(5):
        session.post(f"{BASE_URL}/send_alert", json={
            "message": f"Burst Alert #{i}",
            "regions": ["Delhi", "Mumbai", "Chennai", "Bangalore"]
        })
    
    print("Burst complete. Check Grafana for Queue Depth and Worker Time spikes.")

    print("\n--- [4] Logging out (Metric C) ---")
    session.get(f"{BASE_URL}/logout")
    print("Logged out. Current Admin count should drop.")

if __name__ == "__main__":
    run_comprehensive_test()