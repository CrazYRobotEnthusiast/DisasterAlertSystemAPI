from interfaces import ContactFetcher, DBInterface, AlertDispatcher, AlertTask, MessageSender
import concurrent.futures # Standard library for Thread Pooling
import time
from metrics import WORKER_TIME, ACTIVE_WORKER_THREADS,ALERTS_DISPATCHED

class PhoneNumberFetcher(ContactFetcher):
    """Focuses strictly on phone number retrieval."""
    def __init__(self, db: DBInterface):
        self.db = db

    def fetch_by_region(self, region: str) -> list[str]:
        return self.db.fetch("phone", region)

class RegionContactService:
    """
    Business Logic: Ensures no false positives (Safety).
    Handles deduplication so users don't get 10 alerts for one event.
    """
    def __init__(self, fetcher: ContactFetcher):
        self.fetcher = fetcher

    def get_unique_contacts(self, regions: list[str]) -> set[str]:
        contacts = []
        for region in regions:
            contacts.extend(self.fetcher.fetch_by_region(region))
        return set(contacts)

class AsyncAlertDispatcher(AlertDispatcher):
    """
    Reliability Layer: Uses a queue to handle high traffic.
    Prevents the main application from freezing during massive alerts.
    """
    def __init__(self, queue):
        self.queue = queue

    def dispatch(self, task: AlertTask) -> None:
        # Non-blocking: We just drop it in the queue and return immediately.
        self.queue.push(task)

class AlertWorker:
    """
    Background processor with parallel execution and telemetry instrumentation.
    """
    def __init__(self, sender, max_workers: int = 10):
        self.sender = sender
        self.max_workers = max_workers

    def process_next(self, queue):
        task = queue.pop()
        if not task:
            return

        start_time = time.time()
        
        # G) Thread Utilisation: Set to max during batch processing
        ACTIVE_WORKER_THREADS.set(self.max_workers)
        
        print(f"[WORKER] Starting parallel dispatch for {len(task.recipients)} recipients...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # We pass the region to the sender so it can log Metric I (Regional Distribution)
            # Note: We assume task.regions is a list of regions the alert belongs to
            region_label = ", ".join(task.regions) if hasattr(task, 'regions') else "Unknown"
            
            futures = {
                executor.submit(self.sender.send, contact, task.message): contact 
                for contact in task.recipients
            }
            
            for future in concurrent.futures.as_completed(futures):
                contact = futures[future]
                try:
                    success = future.result()
                    
                    # H, I) Twilio Success Rate & Regional Distribution
                    # We record metrics here if the sender doesn't do it internally
                    status = "success" if success else "failure"
                    ALERTS_DISPATCHED.labels(region=region_label, status=status).inc()
                    
                except Exception as e:
                    print(f"[ERROR] Failed to send to {contact}: {e}")
                    ALERTS_DISPATCHED.labels(region=region_label, status="error").inc()

        # Reset Gauge and Record Timing
        ACTIVE_WORKER_THREADS.set(0) # G
        WORKER_TIME.observe(time.time() - start_time) # F
        
        print("[WORKER] Finished processing task.")


class AlertController:
    """
    Orchestrator for the Alert System (Usability Principle).
    Receives (Message, ListOfRegions) and manages the internal pipeline.
    """
    def __init__(self, contact_service: RegionContactService, dispatcher: AlertDispatcher):
        self.contact_service = contact_service
        self.dispatcher = dispatcher

    def trigger_disaster_alert(self, message: str, regions: list[str]):
        """
        Coordinates the flow from fetching to dispatching.
        """
        print(f"\n[CONTROLLER] Received alert request for: {regions}")
        
        # 1. Fetch & Deduplicate (Safety)
        contacts = self.contact_service.get_unique_contacts(regions)
        
        # 2. Encapsulate into a Task (DTO)
        task = AlertTask(message=message, recipients=contacts,regions=regions)
        
        # 3. Hand over to dispatcher (Reliability)
        self.dispatcher.dispatch(task)
        print(f"[CONTROLLER] Alert task for {len(contacts)} users successfully queued.")