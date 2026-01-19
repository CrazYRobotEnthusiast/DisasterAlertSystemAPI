from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class AlertTask:
    """
    Data Transfer Object (DTO) for safety. 
    Encapsulates the message and target recipients.
    """
    message: str
    recipients: set[str]
    regions: list[str]

class DBInterface(ABC):
    """Contract for database access."""
    @abstractmethod
    def fetch(self, field: str, region: str) -> list[str]:
        pass

class ContactFetcher(ABC):
    """Contract for what data is fetched."""
    @abstractmethod
    def fetch_by_region(self, region: str) -> list[str]:
        pass

class MessageSender(ABC):
    """Contract for the actual hardware/SDK sending the message (e.g., Twilio)."""
    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        pass

class AlertDispatcher(ABC):
    """Contract for how the system handles the sending process (Sync vs Async)."""
    @abstractmethod
    def dispatch(self, task: AlertTask) -> None:
        pass