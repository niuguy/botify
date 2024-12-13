import pytest
from langchain_openai import ChatOpenAI
from botify.agent.agent_factory import AgentFactory
from botify.agent.agent_base import ChatAgent


def test_create_assistant_agent():
    """Test creating an assistant agent with default configuration."""
    llm = ChatOpenAI(model="gpt-4-mini")

    agent = AgentFactory.create_assistant_agent(llm=llm)
    assert agent is not None
    assert isinstance(agent, ChatAgent)

    # assert isinstance(workflow, Graph)


def test_create_agent_with_invalid_type():
    """Test creating an agent with an invalid agent type raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        AgentFactory.create(agent_type="invalid_type")

    assert "Unsupported agent type" in str(exc_info.value)


def test_get_agent_list():
    """Test that get_agent_list returns the correct agent types."""
    agent_types = AgentFactory.get_agent_list()

    assert isinstance(agent_types, list)
