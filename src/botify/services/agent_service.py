from datetime import datetime
from typing import Optional, Dict
from langchain_core.messages import HumanMessage
from botify.agent.agent_factory import AgentFactory
from botify.models.agent_session import AgentSession
from botify.logging.logger import logger
import uuid


class AgentService:
    def __init__(self):
        self.sessions: Dict[str, AgentSession] = {}

    def create_agent(self, agent_type: str, **kwargs) -> AgentSession:
        """Create a new agent and return AgentSession"""  
        agent = AgentFactory.create(agent_type, **kwargs)
        session_id = str(uuid.uuid4())
        
        # Create new agent session
        session = AgentSession(
            session_id=session_id,
            agent_type=agent_type,
            created_at=datetime.now(),
            last_used=datetime.now(),
            metadata=kwargs,  # Store any additional parameters
            agent=agent
        )
        
        # Store session
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[AgentSession]:
        """Retrieve an agent session"""
        return self.sessions.get(session_id)

    def update_session_timestamp(self, session_id: str) -> None:
        """Update last_used timestamp of a session"""
        if session := self.sessions.get(session_id):
            session.last_used = datetime.now()

    async def process_message(self, message: str, session_id: str) -> str:
        """Process a message using the specified agent session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"No active session found for ID: {session_id}")

        try:
            # Update last used timestamp
            self.update_session_timestamp(session_id)
            
            result = session.agent.run(
                {"messages": [HumanMessage(content=message)]},
                config={"configurable": {"session_id": session_id}},
            )
            return result["messages"][-1].content
        except Exception as e:
            logger.error(f"Error processing message in session {session_id}: {str(e)}")
            raise

    def create_reader_agent(self, url: str) -> AgentSession:
        """Specifically create a reader agent"""
        return self.create_agent("reader", url=url)

    def get_available_agents(self) -> list[str]:
        """Get list of available agents"""
        return AgentFactory.get_agent_list()

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> None:
        """Clean up sessions older than specified hours"""
        current_time = datetime.now()
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            age = (current_time - session.last_used).total_seconds() / 3600
            if age > max_age_hours:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
