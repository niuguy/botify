from typing import TypedDict, Dict
from langchain_core.messages import BaseMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, END
from botify.logging.logger import logger
from botify.agent.agent_tool import tools


class AgentState(TypedDict):
    """State definition for the agent graph."""

    messages: list[BaseMessage]
    next: str | None


class AgentModel:
    """Wrapper class for LLM that manages chat history."""

    def __init__(self, llm: ChatOpenAI):
        self.llm = ChatOpenAI(model="gpt-4").bind_tools(tools)
        self._chat_histories: Dict[str, InMemoryChatMessageHistory] = {}

    def get_chat_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """Get or create chat history for a session."""
        if session_id not in self._chat_histories:
            self._chat_histories[session_id] = InMemoryChatMessageHistory()
        return self._chat_histories[session_id]

    def call_llm(
        self, state: MessagesState, config: RunnableConfig
    ) -> list[BaseMessage]:
        logger.info(f"call_llm State: {state}")
        try:
            if (
                "configurable" not in config
                or "session_id" not in config["configurable"]
            ):
                raise ValueError(
                    "Make sure that the config includes the following information: {'configurable': {'session_id': 'some_value'}}"
                )
            chat_history = self.get_chat_history(config["configurable"]["session_id"])
            messages = list(chat_history.messages) + state["messages"]
            ai_message = self.llm.invoke(messages)
            chat_history.add_messages(state["messages"] + [ai_message])
        except Exception as e:
            logger.error(f"Error in call_llm: {e}")
        return {"messages": [ai_message]}

    def should_continue(self, state: MessagesState, config: RunnableConfig) -> bool:
        try:
            aiMessage = state["messages"][-1]
            logger.info(f"Type of aiMessage: {type(aiMessage)}")
            logger.info(f"AiMessage: {aiMessage}")
            logger.info(f"AiMessage tool_calls: {aiMessage.tool_calls}")
            if aiMessage.tool_calls:
                return "tools"
        except Exception as e:
            logger.error(f"Error in should_continue: {e}")
        return END
