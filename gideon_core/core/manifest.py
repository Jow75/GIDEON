from typing import Dict, Any, List
from pydantic import BaseModel, Field

class SkillManifest(BaseModel):
    name: str = Field(..., description="Unique identifier for the skill")
    version: str = Field(..., description="Semantic version string")
    description: str = Field(..., description="Clear description of what the skill does")
    permissions: List[str] = Field(default_factory=list, description="Required system permissions (e.g., fs_read, fs_write, net_out)")
    required_capabilities: List[str] = Field(default_factory=list, description="Required AI capabilities (e.g., coding, reasoning)")
    requires_confirmation: bool = Field(default=False, description="Whether execution requires explicit user confirmation")
    input_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON schema defining expected inputs")
    output_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON schema defining outputs")
    execution_category: str = Field(default="utility", description="Category: utility, web, system, core")
