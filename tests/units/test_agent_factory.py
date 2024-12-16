import pytest
from langchain_openai import ChatOpenAI
from botify.agent.agent_factory import AgentFactory
from botify.agent.agents.base_agent import BaseAgent


def test_create_agent():
    """Test creating an agent with default configuration."""
    llm = ChatOpenAI(model="gpt-4-mini")

    # Create a basic agent
    agent = AgentFactory.create(agent_type="chat", llm=llm)
    assert agent is not None
    assert isinstance(agent, BaseAgent)


def test_create_agent_with_invalid_type():
    """Test creating an agent with an invalid agent type raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        AgentFactory.create(agent_type="invalid_type")

    assert "Unsupported agent type" in str(exc_info.value)


def test_get_available_agents():
    """Test that get_available_agents returns the correct agent types."""
    agent_types = AgentFactory.get_available_agents()

    assert isinstance(agent_types, list)
    assert len(agent_types) > 0  # Should have at least one agent type
    assert all(isinstance(agent_type, str) for agent_type in agent_types)


def test_agent_loading():
    """Test that agents are properly loaded from the agents directory."""
    # First call to ensure agents are loaded
    AgentFactory._load_agents()

    # Check if agent classes dictionary is populated
    assert len(AgentFactory._agent_classes) > 0

    # Verify all loaded classes are subclasses of BaseAgent
    for agent_class in AgentFactory._agent_classes.values():
        assert issubclass(agent_class, BaseAgent)
