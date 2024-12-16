import importlib
import inspect
from pathlib import Path
from typing import Type, Dict
from botify.agent.agents.base_agent import BaseAgent
from langchain_openai import ChatOpenAI


class AgentFactory:
    """Factory class for creating agents with automatic loading."""

    _agent_classes: Dict[str, Type[BaseAgent]] = {}

    @classmethod
    def _load_agents(cls):
        """Automatically load all agent classes from the agents directory."""
        if not cls._agent_classes:
            # Get the directory containing the agent modules
            agents_dir = Path(__file__).parent / "agents"

            # Iterate through all python files in the directory
            for file_path in agents_dir.glob("*_agent.py"):
                if file_path.stem == "base_agent":
                    continue

                # Import the module
                module_name = f"botify.agent.agents.{file_path.stem}"
                module = importlib.import_module(module_name)

                # Find all classes that inherit from BaseAgent
                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, BaseAgent)
                        and obj != BaseAgent
                    ):
                        # Convert class name to agent type (e.g., RAGAgent -> rag)
                        agent_type = name.lower().replace("agent", "")
                        cls._agent_classes[agent_type] = obj

    @classmethod
    def create(cls, agent_type: str, llm: ChatOpenAI = None, **kwargs) -> BaseAgent:
        """Create an agent instance of the specified type."""
        cls._load_agents()

        if agent_type not in cls._agent_classes:
            raise ValueError(f"Unsupported agent type: {agent_type}")

        agent_class = cls._agent_classes[agent_type]

        return agent_class(llm, **kwargs)

    @classmethod
    def get_available_agents(cls) -> list[str]:
        """Get a list of available agent types."""
        cls._load_agents()
        return list(cls._agent_classes.keys())

    @classmethod
    def get_agent_list(cls) -> list[str]:
        """Get a list of available agent types."""
        cls._load_agents()
        return list(cls._agent_classes.keys())
