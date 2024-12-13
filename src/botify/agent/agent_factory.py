from langchain_openai import ChatOpenAI
from langgraph.graph import Graph
from botify.agent.agent_base import ChatAgent
from botify.agent.rag_agent import RAGAgent 
from enum import Enum


class AgentType(Enum):
    ASSISTANT = "assistant"
    RESEARCHER = "researcher"
    READER = "reader"
    SCHEDULER = "scheduler"


class AgentFactory:
    """Factory class for creating LangGraph-based agents."""

    @classmethod
    def create_assistant_agent(cls, llm: ChatOpenAI) -> Graph:
        agent_model = ChatAgent(llm)

        return agent_model

    @classmethod
    def create_rag_agent(cls, llm: ChatOpenAI) -> Graph:
        """Creates a RAG-based agent workflow.

        Args:
            llm (ChatOpenAI): The language model to use for the agent

        Returns:
            Graph: Compiled workflow graph for RAG operations
        """
        pass
        # # Initialize RAG agent
        # rag_agent = RAGAgent()

        # # Create workflow
        # workflow = StateGraph(RagAgentState)

        # # Define the nodes we will cycle between
        # workflow.add_node("agent", rag_agent.agent)  # Agent decision node
        # workflow.add_node("retrieve", retriever_tool_node)  # Retrieval node
        # workflow.add_node("rewrite", rag_agent.rewrite)  # Query rewriting node
        # workflow.add_node("generate", rag_agent.generate)  # Response generation node

        # # Initial edge: Start -> Agent
        # workflow.add_edge(START, "agent")

        # # Agent decision edges
        # workflow.add_conditional_edges(
        #     "agent",
        #     tools_condition,
        #     {
        #         "tools": "retrieve",  # If tools needed, go to retrieve
        #         END: END,  # If no tools needed, end
        #     },
        # )

        # # Retrieval result edges
        # workflow.add_conditional_edges(
        #     "retrieve",
        #     rag_agent.grade_documents,
        #     {
        #         "generate": "generate",  # If documents relevant, generate response
        #         "rewrite": "rewrite",    # If documents not relevant, rewrite query
        #     }
        # )

        # # Final edges
        # workflow.add_edge("generate", END)  # Generation complete -> End
        # workflow.add_edge("rewrite", "agent")  # After rewrite -> Back to agent

        # return workflow.compile()

    @classmethod
    def create(
        cls,
        agent_type: str,
        llm: ChatOpenAI = ChatOpenAI(model="gpt-4o-mini"),
        url: str = None,
    ) -> Graph:
        if agent_type == AgentType.ASSISTANT.value:
            return ChatAgent(llm)
        elif agent_type == AgentType.READER.value:
            return RAGAgent(llm, url)
        else:
            raise ValueError(f"Unsupported agent type: {agent_type}")

    @classmethod
    def get_agent_list(cls) -> list[AgentType]:
        """Get a list of available agent types."""
        return [agent.value for agent in AgentType]
