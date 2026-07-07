import pytest
from orchestration.research import ResearchAgent
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_research_agent_flow():
    # Mock router
    mock_router = AsyncMock()
    # First response: queries
    # Second response: final report
    mock_router.execute_task.side_effect = [
        "['query 1', 'query 2']",
        "This is the synthesized research report."
    ]
    
    # Mock execution service
    mock_execution = AsyncMock()
    mock_execution.skills = {"web_search": MagicMock()}
    mock_execution.execute_skill.return_value = "Mocked search result"
    
    research_agent = ResearchAgent(router=mock_router, execution_service=mock_execution)
    
    report = await research_agent.conduct_research(topic="Test Topic")
    
    assert "This is the synthesized research report." in report
    assert mock_router.execute_task.call_count == 2
    assert mock_execution.execute_skill.call_count == 2
