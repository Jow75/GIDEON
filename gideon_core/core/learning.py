from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import datetime
import logging
from core.event_bus import EventBus, Event
from memory.base import LongTermMemoryStore
from orchestration.router import AIOperationsRouter

logger = logging.getLogger(__name__)

class ExperienceRecord(BaseModel):
    id: str = Field(..., description="Unique ID for this experience")
    type: str = Field(..., description="factual_knowledge, user_preference, reusable_workflow, execution_history, temporary_observation")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    original_objective: str
    execution_plan: List[Dict[str, Any]] = []
    tools_used: List[str] = []
    reasoning_summary: str = ""
    outcome: str = ""
    failures_encountered: List[str] = []
    user_corrections: List[str] = []
    lessons_learned: str = ""
    confidence_score: float = 1.0
    reusable_workflow: Optional[Dict[str, Any]] = None
    associated_project: Optional[str] = None
    associated_memories: List[str] = []

class LearningService:
    """
    Evaluates completed tasks and system interactions to extract structured,
    long-term value before committing it to permanent memory (LTM).
    """
    def __init__(self, event_bus: EventBus, ltm: LongTermMemoryStore, router: AIOperationsRouter):
        self.event_bus = event_bus
        self.ltm = ltm
        self.router = router
        
        # Subscribe to task completion events
        self.event_bus.subscribe("task_completed", self._on_task_completed)

    async def _on_task_completed(self, event: Event):
        """Analyze task completion to extract valuable experiences."""
        payload = event.payload
        logger.info(f"LearningService analyzing completed task: {payload.get('objective')}")
        
        # In a full implementation, we'd prompt the router (LLM) to extract lessons and decide the type
        # For this foundation, we construct a base record
        
        record = ExperienceRecord(
            id=f"exp_{datetime.datetime.now().timestamp()}",
            type="execution_history", # default
            original_objective=payload.get("objective", "Unknown"),
            outcome=payload.get("outcome", "Success"),
            tools_used=payload.get("tools_used", []),
            failures_encountered=payload.get("failures", []),
            reasoning_summary=payload.get("summary", "No summary provided.")
        )
        
        # Decide if we should promote to permanent memory
        if record.type in ["factual_knowledge", "user_preference", "reusable_workflow"]:
            await self._promote_to_ltm(record)
        else:
            # Temporary observations or basic execution history might just be logged
            logger.debug(f"Experience {record.id} categorized as {record.type}, bypassing permanent LTM.")

    async def _promote_to_ltm(self, record: ExperienceRecord):
        """Promote a structured experience into permanent ChromaDB storage."""
        # Convert record to searchable text
        searchable_text = f"Objective: {record.original_objective}\nOutcome: {record.outcome}\nLessons: {record.lessons_learned}"
        
        # Store with structured metadata
        metadata = {
            "type": record.type,
            "confidence": record.confidence_score,
            "project": record.associated_project or "none"
        }
        
        await self.ltm.store_experience(searchable_text, metadata=metadata)
        logger.info(f"Promoted experience {record.id} to LTM.")
