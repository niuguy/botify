import pytest
from unittest.mock import Mock, patch
from langchain_core.messages import HumanMessage, AIMessage
from botify.services.agent_service import AgentService


@pytest.fixture
def agent_service():
    return AgentService()


@pytest.fixture
def mock_agent():
    agent = Mock()
    agent.run.return_value = {
        "messages": [
            HumanMessage(content="test message"),
            AIMessage(content="test response"),
        ]
    }
    return agent


class TestAgentService:
    @patch("botify.services.agent_service.AgentFactory")
    def test_create_agent_success(self, mock_factory, agent_service):
        # Arrange
        mock_factory.create.return_value = Mock()
        agent_type = "test_agent"

        # Act
        session_id, agent = agent_service.create_agent(agent_type)

        # Assert
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        mock_factory.create.assert_called_once_with(agent_type)

    @patch("botify.services.agent_service.AgentFactory")
    def test_create_agent_with_kwargs(self, mock_factory, agent_service):
        # Arrange
        mock_factory.create.return_value = Mock()
        agent_type = "test_agent"
        kwargs = {"param1": "value1", "param2": "value2"}

        # Act
        session_id, agent = agent_service.create_agent(agent_type, **kwargs)

        # Assert
        mock_factory.create.assert_called_once_with(agent_type, **kwargs)

    @patch("botify.services.agent_service.AgentFactory")
    def test_create_agent_failure(self, mock_factory, agent_service):
        # Arrange
        mock_factory.create.side_effect = Exception("Test error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            agent_service.create_agent("test_agent")
        assert str(exc_info.value) == "Test error"

    @patch("botify.services.agent_service.AgentFactory")
    def test_create_reader_agent(self, mock_factory, agent_service):
        # Arrange
        mock_factory.create.return_value = Mock()
        test_url = "http://test.com"

        # Act
        session_id, agent = agent_service.create_reader_agent(test_url)

        # Assert
        mock_factory.create.assert_called_once_with("reader", url=test_url)

    @patch("botify.services.agent_service.AgentFactory")
    def test_get_available_agents(self, mock_factory, agent_service):
        # Arrange
        expected_agents = ["agent1", "agent2"]
        mock_factory.get_agent_list.return_value = expected_agents

        # Act
        result = agent_service.get_available_agents()

        # Assert
        assert result == expected_agents
        mock_factory.get_agent_list.assert_called_once()

    async def test_process_message_success(self, agent_service, mock_agent):
        # Arrange
        message = "test message"
        session_id = "test_session"
        expected_response = "test response"

        # Act
        result = await agent_service.process_message(message, mock_agent, session_id)

        # Assert
        assert result == expected_response
        mock_agent.run.assert_called_once()
        call_args = mock_agent.run.call_args[0][0]
        assert isinstance(call_args["messages"][0], HumanMessage)
        assert call_args["messages"][0].content == message

    async def test_process_message_failure(self, agent_service, mock_agent):
        # Arrange
        mock_agent.run.side_effect = Exception("Test error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await agent_service.process_message("test", mock_agent, "test_session")
        assert str(exc_info.value) == "Test error"

