import pytest
from pathlib import Path
from langchain_openai import ChatOpenAI
from langgraph.graph import Graph
from botify.agent.factory import AgentFactory

def test_create_prompt_agent():
    """Test creating a prompt agent with default configuration."""
    llm = ChatOpenAI(model="gpt-4-mini")
    system_message = "You are a helpful assistant."
    
    workflow = AgentFactory.create_prompt_agent(
        llm=llm,
        system_message=system_message
    )
    
    assert isinstance(workflow, Graph)

def test_create_agent_with_valid_type():
    """Test creating an agent with a valid agent type."""
    workflow = AgentFactory.create(
        agent_type="prompt",
        agent_name="test_agent",
        system_message="You are a helpful assistant."
    )
    
    assert isinstance(workflow, Graph)

def test_create_agent_with_invalid_type():
    """Test creating an agent with an invalid agent type raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        AgentFactory.create(
            agent_type="invalid_type",
            agent_name="test_agent"
        )
    
    assert "Unsupported agent type" in str(exc_info.value)

def test_agent_configs_loading():
    """Test that agent configurations are loaded correctly."""
    configs = AgentFactory._load_agent_configs()
    
    assert isinstance(configs, dict)
    assert "prompt" in configs
    assert "system_message" in configs["prompt"]
    assert "node_name" in configs["prompt"] 