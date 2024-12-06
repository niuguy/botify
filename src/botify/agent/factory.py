from typing import Dict, Annotated, TypedDict
from langchain_core.messages import BaseMessage, SystemMessage
# from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI


from langgraph.graph import StateGraph, Graph, START, END
from langchain_core.prompts import ChatPromptTemplate

class AgentState(TypedDict):
    """State definition for the agent graph."""
    messages: list[BaseMessage]
    next: str | None

class AgentFactory:
    """Factory class for creating LangGraph-based agents."""
    
    _AGENT_CONFIGS = {
        "prompt": {
            "system_message": "You are a helpful AI assistant. Respond to the user's request.",
            "node_name": "chatbot"
        },
        # Can add more agent types here with their specific configurations
    }

    @classmethod
    def create_prompt_agent(
        cls, 
        llm: ChatOpenAI,
        system_message: str,
        node_name: str = "process"
    ) -> Graph:
        """Create a basic prompt agent using LangGraph.
        
        Args:
            llm: The language model to use
            system_message: The system message defining agent's behavior
            node_name: Name for the processing node
            
        Returns:
            A LangGraph workflow
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "{input}"),
        ])

        def process(state: AgentState) -> AgentState:
            messages = state["messages"]
            last_message = messages[-1].content
            
            response = llm.invoke(prompt.format_messages(input=last_message))
            messages.append(response)
            
            return {"messages": messages, "next": None}

        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add the processing node
        workflow.add_node(node_name, process)
        
        # Set the entry point
        workflow.set_entry_point(node_name)
        
        # # Add the end condition
        workflow.add_edge(START, node_name)
        workflow.add_edge(node_name, END)
        
        return workflow.compile()

    @classmethod
    def create(cls, agent_type: str, llm: ChatOpenAI = ChatOpenAI(model="gpt-4o-mini"), **kwargs) -> Graph:
        """Create a new LangGraph agent instance.
        
        Args:
            agent_type: Type of agent to create (e.g., 'prompt')
            llm: Language model to use with the agent
            **kwargs: Additional configuration for the agent
            
        Returns:
            A compiled LangGraph workflow
            
        Raises:
            ValueError: If agent_type is not supported
        """
        if agent_type not in cls._AGENT_CONFIGS:
            raise ValueError(f"Unsupported agent type: {agent_type}")

        config = cls._AGENT_CONFIGS[agent_type].copy()
        
        # Override default config with any provided kwargs
        system_message = kwargs.get('system_message', config['system_message'])
        node_name = kwargs.get('node_name', config['node_name'])

        if agent_type == "prompt":
            return cls.create_prompt_agent(
                llm=llm,
                system_message=system_message,
                node_name=node_name
            )
