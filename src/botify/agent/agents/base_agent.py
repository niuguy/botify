# src/botify/agent/agent_base.py
from abc import ABC, abstractmethod
from typing import TypedDict
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import Graph



class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    @abstractmethod
    def generate_flow(self) -> Graph:
        """Generate the workflow graph for the agent."""
        pass

    @abstractmethod
    def run(self, inputs: dict, config: RunnableConfig):
        """Run the agent workflow."""
        pass
