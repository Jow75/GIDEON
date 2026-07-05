from typing import List, Dict, Any
import json
import re
from providers.base import Message
from orchestration.router import AIOperationsRouter
from orchestration.planner import PlannerAgent
from orchestration.coder import CoderAgent
from skills import get_available_skills

class CommanderAgent:
    """
    The central agent that receives intent from the Consciousness layer,
    determines which skills to use, delegates to sub-agents, and formulates the final response.
    """
    def __init__(self, router: AIOperationsRouter):
        self.router = router
        self.skills = get_available_skills()
        self.planner = PlannerAgent(router)
        self.coder = CoderAgent(router)

    def _format_skills_prompt(self) -> str:
        prompt = "You have access to the following skills and sub-agents:\n"
        for name, skill in self.skills.items():
            prompt += f"- {name}: {skill.description}\n"
        prompt += "- delegate_to_planner: Break down a complex, multi-step task.\n"
        prompt += "- delegate_to_coder: Write or review code.\n"

        prompt += """\nTo use a skill or sub-agent, output ONLY a JSON object in this exact format, wrapped in triple backticks:
```json
{
  "skill_name": "name_of_skill",
  "arguments": {"arg1": "value1"}
}
```
If you do not need to use a skill, simply reply to the user naturally."""
        return prompt

    def process(self, context_messages: List[Message], world_state: str = "") -> str:
        skills_prompt = self._format_skills_prompt()

        messages = context_messages.copy()
        messages.insert(-1, Message(role="system", content=skills_prompt))

        response_text = self.router.execute_task(required_tags=["commander"], messages=messages)

        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if not json_match and response_text.strip().startswith('{') and response_text.strip().endswith('}'):
            try:
                action = json.loads(response_text.strip())
                if "skill_name" in action:
                    json_match = type('obj', (object,), {'group': lambda self, n: response_text.strip()})()
            except:
                pass

        if json_match:
            try:
                action = json.loads(json_match.group(1))
                skill_name = action.get("skill_name")
                args = action.get("arguments", {})

                result = ""
                if skill_name == "delegate_to_planner":
                    objective = args.get("objective", "Unknown objective")
                    plan = self.planner.generate_plan(objective, world_state)
                    result = f"Planner generated the following steps:\n{json.dumps(plan, indent=2)}"
                elif skill_name == "delegate_to_coder":
                    prompt = args.get("prompt", "")
                    code = self.coder.write_code(prompt)
                    result = f"Coder generated the following code:\n{code}"
                elif skill_name in self.skills:
                    result = self.skills[skill_name].execute(**args)
                else:
                    return f"[Error: Unknown skill/agent '{skill_name}']"

                follow_up_messages = messages.copy()
                follow_up_messages.append(Message(role="assistant", content=response_text))
                follow_up_messages.append(Message(role="system", content=f"Execution result:\n{result}\n\nProvide the final response to the user based on this result."))

                return self.router.execute_task(required_tags=["commander"], messages=follow_up_messages)
            except json.JSONDecodeError:
                pass

        return response_text
