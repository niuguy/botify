from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, Graph, START, END
import yaml
from pathlib import Path
from botify.agent.agent_base import AgentModel
from botify.agent.agent_tool import tool_node
from botify.agent.agent_base import AgentState
from enum import Enum, auto


class AgentType(Enum):
    ASSISTANT = "assistant"
    RESEARCHER = "researcher"
    READER = "reader"
    SCHEDULER = "scheduler"

class AgentFactory:
    """Factory class for creating LangGraph-based agents."""

    # def _load_agent_configs() -> dict:
    #     """Load agent configurations from YAML file."""
    #     config_path = Path(__file__).parent / "configs" / "agent_configs.yaml"
    #     with open(config_path, "r") as f:
    #         return yaml.safe_load(f)

    # _AGENT_CONFIGS = _load_agent_configs()

    @classmethod
    def create_assistant_agent(
        cls, llm: ChatOpenAI
    ) -> Graph:
        agent_model = AgentModel(llm)
        workflow = StateGraph(AgentState)

        workflow.add_node("agent", agent_model.call_llm)
        workflow.add_node("tools", tool_node)

        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent", agent_model.should_continue, ["tools", END]
        )
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    @classmethod
    def create(
        cls,
        agent_type: str,
        llm: ChatOpenAI = ChatOpenAI(model="gpt-4o-mini"),
    ) -> Graph:
        # if agent_type not in AgentType.value:
        #     raise ValueError(f"Unsupported agent type: {agent_name}")

        # agent_config = cls._AGENT_CONFIGS[agent_name.value].copy()
        # system_message = kwargs.get("system_message", agent_config["system_message"])
        # node_name = kwargs.get("node_name", agent_config["node_name"])
        # agent_type = kwargs.get("agent_type", agent_config["type"])

        if agent_type == AgentType.ASSISTANT.value:
            return cls.create_assistant_agent(
                llm=llm
            )
        else:
            raise ValueError(f"Unsupported agent type: {agent_type}")

    @classmethod
    def get_agent_list(cls) -> list[AgentType]:
        """Get a list of available agent types."""
        return [agent.value for agent in AgentType]
