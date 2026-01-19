import sqlite3
from interfaces import DBInterface, MessageSender
import os
from dotenv import load_dotenv
from twilio.rest import Client
from metrics import QUEUE_DEPTH, ALERTS_DISPATCHED

load_dotenv()

class SQLiteDB(DBInterface):
    def __init__(self, db_path: str = "disaster_alert.db"):
        self.db_path = db_path

    def fetch(self, field: str, region: str) -> list[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = f"SELECT {field} FROM users WHERE region = ?"
            cursor.execute(query, (region,))
            return [row[0] for row in cursor.fetchall() if row[0]]

class ConsoleMessageSender(MessageSender):
    def send(self, recipient: str, message: str) -> bool:
        print(f"[SMS API] Sending to {recipient}: {message}")
        return True

class InMemoryTaskQueue:
    def __init__(self):
        self.queue = []

    def push(self, task):
        self.queue.append(task)
        QUEUE_DEPTH.set(len(self.queue))
        

    def pop(self):
        task= self.queue.pop(0) if self.queue else None
        QUEUE_DEPTH.set(len(self.queue))
        return task

    def is_empty(self):
        return len(self.queue) == 0

class TwilioMessageSender(MessageSender):
    """
    Concrete Adapter for Twilio SMS API.
    Follows SRP: Responsible only for Twilio communication.
    """
    def __init__(self):
        # Fetching credentials from environment variables for security
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.messaging_service_sid = os.getenv('TWILIO_MESSAGING_SERVICE_SID')
        
        # Initializing the Twilio Client
        try:
            self.client = Client(self.account_sid, self.auth_token)
        except Exception as e:
            print(f"[CRITICAL] Twilio Initialization Failed: {e}")
            self.client = None

    def send(self, recipient: str, message_body: str, region: str = "unknown") -> bool:
        """
        Sends an SMS via Twilio Messaging Service.
        Ensures Reliability by catching network/API exceptions.
        """
        if not self.client:
            print("[ERROR] Twilio client not initialized.")
            return False

        try:
            # Mapping Twilio SDK call to our MessageSender interface
            message = self.client.messages.create(
                messaging_service_sid=self.messaging_service_sid,
                body=message_body,
                to=recipient
            )
            #ALERTS_DISPATCHED.labels(region=region, status='success').inc()
            print(f"[TWILIO SUCCESS] SID: {message.sid} sent to {recipient}")
            return True
            
        except Exception as e:
            # Safety Principle: Log error so we know which messages failed
            #ALERTS_DISPATCHED.labels(region=region, status='failure').inc()
            print(f"[TWILIO FAILURE] Could not send to {recipient}: {e}")
            return False

class SQLiteAuthenticator:
    """Handles verification of Admin credentials."""
    def __init__(self, db_path: str = "disaster_alert.db"):
        self.db_path = db_path

    def authenticate(self, username, password) -> bool:
        """Checks if username/password exists in the admins table."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT 1 FROM admins WHERE username = ? AND password = ?"
            cursor.execute(query, (username, password))
            return cursor.fetchone() is not None