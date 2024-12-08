from typing import TypedDict, Dict
from langchain_core.messages import BaseMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableConfig

# from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from langchain_core.tools import tool

from langgraph.prebuilt import ToolNode

from langgraph.graph import StateGraph, Graph,MessagesState, END, START
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage

import yaml
from pathlib import Path
from botify.logging.logger import logger

@tool
def get_weather(location: str):
    """Call to get the current weather."""
    logger.info(f"get_weather location: {location}")
    if location.lower() in ["sf", "san francisco"]:
        return "It's 60 degrees and foggy."
    else:
        return "It's 90 degrees and sunny."
    
@tool
def get_coolest_cities():
    """Get a list of coolest cities"""
    return "nyc, sf"


tools = [get_weather, get_coolest_cities]
tool_node = ToolNode(tools)


class AgentState(TypedDict):
    """State definition for the agent graph."""

    messages: list[BaseMessage]
    next: str | None


class AgentModel:
    """Wrapper class for LLM that manages chat history."""
    def __init__(self, llm: ChatOpenAI):
        self.llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)
        self._chat_histories: Dict[str, InMemoryChatMessageHistory] = {}

    def get_chat_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """Get or create chat history for a session."""
        if session_id not in self._chat_histories:
            self._chat_histories[session_id] = InMemoryChatMessageHistory()
        return self._chat_histories[session_id]
    
    def call_llm(self, state: MessagesState, config: RunnableConfig) -> list[BaseMessage]:
        # Make sure that config is populated with the session id
        logger.info(f"call_llm State: {state}")
        try:
            if "configurable" not in config or "session_id" not in config["configurable"]:
                raise ValueError(
                    "Make sure that the config includes the following information: {'configurable': {'session_id': 'some_value'}}"
            )
            # Fetch the history of messages and append to it any new messages.
            chat_history = self.get_chat_history(config["configurable"]["session_id"])
            messages = list(chat_history.messages) + state["messages"]
            ai_message = self.llm.invoke(messages)
            # Finally, update the chat message history to include
            # the new input message from the user together with the
            # repsonse from the model.
            chat_history.add_messages(state["messages"] + [ai_message])
        except Exception as e:
            logger.error(f"Error in call_llm: {e}")
        return {"messages": [ai_message]}

    def should_continue(self, state: MessagesState, config: RunnableConfig) -> bool:
        try:
            aiMessage = state["messages"][-1]
            # what is the type of aiMessage?
            logger.info(f"Type of aiMessage: {type(aiMessage)}")    
            logger.info(f"AiMessage: {aiMessage}")
            logger.info(f"AiMessage tool_calls: {aiMessage.tool_calls}")
            # last_message = messages[-1]
            if aiMessage.tool_calls:
                return "tools"
        except Exception as e:
            logger.error(f"Error in should_continue: {e}")  
        return END



    # def invoke(self, messages: list[BaseMessage], config: dict) -> BaseMessage:
    #     """Process messages with chat history context."""
    #     session_id = config.get("configurable", {}).get("session_id")
    #     if not session_id:
    #         raise ValueError("Session ID is required in config")

    #     chat_history = self.get_chat_history(session_id)
        
    #     # Combine history with current messages
    #     full_messages = list(chat_history.messages) + messages
        
    #     # Get response from LLM
    #     response = self.llm.invoke(full_messages)
        
    #     # Update chat history
    #     chat_history.add_messages(messages + [response])
        
    #     return response


class AgentFactory:
    """Factory class for creating LangGraph-based agents."""

    def _load_agent_configs() -> dict:
        """Load agent configurations from YAML file."""
        config_path = Path(__file__).parent / "configs" / "agent_configs.yaml"
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    _AGENT_CONFIGS = _load_agent_configs()

    @classmethod
    def create_prompt_agent(
        cls, llm: ChatOpenAI, system_message: str, node_name: str = "process"
    ) -> Graph:
        """Create a basic prompt agent using LangGraph.

        Args:
            llm: The language model to use
            system_message: The system message defining agent's behavior
            node_name: Name for the processing node

        Returns:
            A LangGraph workflow
        """
        # Create agent model with history management
        agent_model = AgentModel(llm)

        # Create the graph
        workflow = StateGraph(AgentState)

        # Add the processing node
        workflow.add_node("agent", agent_model.call_llm)
        workflow.add_node("tools", tool_node)

        # Set the entry point
        # workflow.set_entry_point("agent")
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", agent_model.should_continue, ["tools", END])
        workflow.add_edge("tools", "agent")

        # # Add the end condition
        # workflow.set_finish_point(node_name)

        return workflow.compile()
    


    @classmethod
    def create(
        cls,
        agent_name: str,
        llm: ChatOpenAI = ChatOpenAI(model="gpt-4-turbo"),
        **kwargs,
    ) -> Graph:
        """
        Create a new LangGraph agent instance.

        Args:
            agent_name: Name of the agent to create
            llm: Language model to use with the agent
            **kwargs: Additional configuration for the agent

        Returns:
            A compiled LangGraph workflow
        """
        if agent_name not in cls._AGENT_CONFIGS:
            raise ValueError(f"Unsupported agent type: {agent_name}")

        agent_config = cls._AGENT_CONFIGS[agent_name].copy()

        # Override default config with any provided kwargs
        system_message = kwargs.get("system_message", agent_config["system_message"])
        node_name = kwargs.get("node_name", agent_config["node_name"])
        agent_type = kwargs.get("agent_type", agent_config["type"])
    

        if agent_type == "prompt":
            return cls.create_prompt_agent(llm=llm, system_message=system_message, node_name=node_name)

    @classmethod
    def get_agent_list(cls) -> list[str]:
        """Get a list of available agent types."""
        return list(cls._AGENT_CONFIGS.keys())
        
