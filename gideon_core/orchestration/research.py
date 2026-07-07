import logging
from typing import List
from providers.base import Message
from orchestration.router import AIOperationsRouter

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    Coordinates deep research by breaking down a topic into queries,
    fetching information (via web or internal semantic memory),
    and synthesizing a cohesive report.
    """
    def __init__(self, router: AIOperationsRouter, execution_service=None):
        self.router = router
        self.execution = execution_service

    async def conduct_research(self, topic: str, context: str = "") -> str:
        """Perform comprehensive research on a specific topic."""
        logger.info(f"Starting research on topic: {topic}")
        
        # 1. Ask LLM to generate search queries
        query_prompt = f"""You are a research assistant. The user wants to research: "{topic}".
Context: {context}

Generate exactly 3 specific search queries to gather comprehensive information on this topic.
Format as a Python list of strings."""
        
        messages = [Message(role="system", content=query_prompt)]
        queries_response = await self.router.execute_task(required_tags=["reasoning"], messages=messages)
        
        queries = self._parse_queries(queries_response, topic)
        
        # 2. Execute queries via WebSearch skill
        raw_results = []
        if self.execution and "web_search" in self.execution.skills:
            for q in queries:
                res = await self.execution.execute_skill("web_search", query=q)
                raw_results.append(f"Query: {q}\nResult: {res}")
        else:
            raw_results.append("WebSearch skill not available. Cannot perform external research.")
            
        combined_results = "\n\n".join(raw_results)
        
        # 3. Synthesize the final report
        synth_prompt = f"""You are a research synthesis engine.
Synthesize the following raw research results into a concise, accurate report about "{topic}".

Raw Results:
{combined_results}

Focus on facts, actionable insights, and highlight any contradictory information."""
        
        synth_messages = [Message(role="system", content=synth_prompt)]
        report = await self.router.execute_task(required_tags=["reasoning", "conversation"], messages=synth_messages)
        
        return report

    def _parse_queries(self, response: str, topic: str) -> List[str]:
        try:
            import ast
            # Simple attempt to find list representation
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end != 0:
                return ast.literal_eval(response[start:end])
        except Exception as e:
            logger.warning(f"Failed to parse queries: {e}")
            
        return [topic]
