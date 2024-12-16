from botify.agent.agents.base_agent import BaseAgent
from langchain_core.runnables import RunnableConfig
from langgraph.graph import Graph
from langchain_openai import ChatOpenAI


class ResearcherAgent(BaseAgent):
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)

    def generate_flow(self) -> Graph:
        pass

    def run(self, inputs: dict, config: RunnableConfig):
        return self.generate_flow().invoke(inputs, config)
