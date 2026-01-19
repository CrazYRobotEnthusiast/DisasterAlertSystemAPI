import threading
import time
from infrastructure import SQLiteDB, ConsoleMessageSender, InMemoryTaskQueue
from domain import (
    PhoneNumberFetcher, 
    RegionContactService, 
    AsyncAlertDispatcher, 
    AlertWorker,
    AlertController
)

def worker_loop(worker, queue):
    """
    Function meant to run in a background thread to 
    continuously process the queue.
    """
    print("[SYSTEM] Background Worker Thread Started.")
    while True:
        worker.process_next(queue)
        time.sleep(1) # Poll the queue every second

def run():
    # 1. Setup
    db = SQLiteDB()
    queue = InMemoryTaskQueue()
    sender = ConsoleMessageSender()
    
    fetcher = PhoneNumberFetcher(db)
    service = RegionContactService(fetcher)
    dispatcher = AsyncAlertDispatcher(queue)
    
    # Worker configured with 5 parallel threads for SMS sending
    worker = AlertWorker(sender, max_workers=5)
    controller = AlertController(service, dispatcher)

    # 2. Start the Worker Loop in a SEPARATE Background Thread
    # This ensures the Controller remains responsive (Usability)
    bg_thread = threading.Thread(target=worker_loop, args=(worker, queue), daemon=True)
    bg_thread.start()

    # 3. Simulate UI interaction
    print("[UI] System ready. Enter regions for alert.")
    
    # The Controller returns almost instantly because it only pushes to the queue
    controller.trigger_disaster_alert(
        message="URGENT: Earthquake alert!", 
        regions=["Delhi", "Mumbai"]
    )

    # Keep the main thread alive for a few seconds to see the worker output
    time.sleep(5)
    print("[UI] Main process exiting.")

if __name__ == "__main__":
    run()