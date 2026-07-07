from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    """A standard event passed over the EventBus."""
    type: str
    source: str
    payload: Dict[str, Any]
    timestamp: datetime = None
    node_id: str = "local" # Added for distributed tracking
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
