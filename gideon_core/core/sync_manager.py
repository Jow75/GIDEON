import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import uuid
import os
from pydantic import BaseModel
from core.event_bus import EventBus, Event
from config.settings import settings

logger = logging.getLogger(__name__)

class StateMetadata(BaseModel):
    node_id: str
    cluster_id: str
    timestamp: datetime
    version: int
    event_id: str
    parent_version: Optional[int] = None

class SyncManager:
    """
    Manages distributed state synchronization for the world_state.
    Implements a Last-Write-Wins (LWW) resolution strategy.
    """
    def __init__(self, event_bus: EventBus, initial_state: Dict[str, Any] = None):
        self.event_bus = event_bus
        self.world_state: Dict[str, Any] = initial_state or {}
        
        # Metadata tracking per key in the world state
        self.metadata: Dict[str, StateMetadata] = {}
        self.node_id = settings.node_id
        self.cluster_id = "default_cluster"
        self.current_version = 0
        
        self._register_subscriptions()

    def _register_subscriptions(self):
        self.event_bus.subscribe("state_sync", self._handle_state_sync)
        self.event_bus.subscribe("state_snapshot_request", self._handle_snapshot_request)
        self.event_bus.subscribe("state_snapshot_response", self._handle_snapshot_response)

    async def update_state(self, key: str, value: Any, source_node: str = None) -> bool:
        """
        Local mutation entrypoint. Mutates state and broadcasts the delta.
        Returns True if the state was updated.
        """
        offset_ms = int(os.environ.get("TIME_OFFSET_MS", 0))
        now = datetime.now(timezone.utc) + timedelta(milliseconds=offset_ms)
        source = source_node or self.node_id
        self.current_version += 1
        
        meta = StateMetadata(
            node_id=source,
            cluster_id=self.cluster_id,
            timestamp=now,
            version=self.current_version,
            event_id=str(uuid.uuid4()),
            parent_version=self.metadata.get(key).version if key in self.metadata else None
        )
        
        # Apply locally
        self.world_state[key] = value
        self.metadata[key] = meta
        
        # Broadcast delta
        await self.event_bus.publish(Event(
            type="state_sync",
            source=self.node_id,
            payload={
                "key": key,
                "value": value,
                "metadata": meta.model_dump(mode="json")
            }
        ))
        return True

    async def _handle_state_sync(self, event: Event):
        """Handle incoming delta from another node."""
        payload = event.payload
        key = payload["key"]
        value = payload["value"]
        
        # Avoid processing our own broadcasts if they loop back
        meta_data = payload["metadata"]
        if meta_data["node_id"] == self.node_id:
            return
            
        incoming_meta = StateMetadata(**meta_data)
        
        # Last-Write-Wins Strategy
        if key in self.metadata:
            local_meta = self.metadata[key]
            if incoming_meta.timestamp <= local_meta.timestamp:
                logger.debug(f"Conflict detected for {key}. Local timestamp is newer. Ignoring incoming.")
                await self.event_bus.publish(Event(
                    type="state_conflict_detected",
                    source=self.node_id,
                    payload={"key": key, "winner_node": local_meta.node_id, "loser_node": incoming_meta.node_id}
                ))
                return

        # Accept incoming change
        self.world_state[key] = value
        self.metadata[key] = incoming_meta
        logger.debug(f"State synced from {incoming_meta.node_id}: {key} -> {value}")
        
        await self.event_bus.publish(Event(
            type="state_sync_complete",
            source=self.node_id,
            payload={"key": key, "version": incoming_meta.version}
        ))

    async def request_snapshot(self, target_node: str = "any"):
        """Request a full state snapshot from the cluster."""
        await self.event_bus.publish(Event(
            type="state_snapshot_request",
            source=self.node_id,
            payload={"requester": self.node_id, "target": target_node}
        ))

    async def _handle_snapshot_request(self, event: Event):
        """Respond to a snapshot request with our full state."""
        requester = event.payload.get("requester")
        target = event.payload.get("target")
        
        if requester == self.node_id:
            return # Don't respond to our own request
            
        if target != "any" and target != self.node_id:
            return
            
        metadata_dump = {k: v.model_dump(mode="json") for k, v in self.metadata.items()}
        await self.event_bus.publish(Event(
            type="state_snapshot_response",
            source=self.node_id,
            payload={
                "target": requester,
                "world_state": self.world_state,
                "metadata": metadata_dump
            }
        ))

    async def _handle_snapshot_response(self, event: Event):
        """Merge an incoming full snapshot using LWW."""
        target = event.payload.get("target")
        if target != self.node_id:
            return
            
        incoming_state = event.payload.get("world_state", {})
        incoming_meta = event.payload.get("metadata", {})
        
        for key, value in incoming_state.items():
            meta = incoming_meta.get(key)
            if not meta:
                continue
                
            in_meta = StateMetadata(**meta)
            
            # LWW Check
            if key in self.metadata:
                if in_meta.timestamp <= self.metadata[key].timestamp:
                    continue
                    
            self.world_state[key] = value
            self.metadata[key] = in_meta
            
        logger.info(f"Successfully processed full state snapshot from {event.source}")
