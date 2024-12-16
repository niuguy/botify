from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentSession:
    session_id: str
    agent_type: str
    created_at: datetime
    last_used: datetime
    metadata: dict
    agent: object  # The actual agent instance
