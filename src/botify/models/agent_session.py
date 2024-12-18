from dataclasses import dataclass
from datetime import datetime
from botify.agent.agents.base_agent import BaseAgent

@dataclass
class AgentSession:
    session_id: str
    agent_type: str
    created_at: datetime
    last_used: datetime
    metadata: dict
    agent: BaseAgent  # The actual agent instance
