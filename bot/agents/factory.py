from langchain.agents import AgentType, create_structured_chat_agent
from langchain.prompts.chat import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
# from lib.config.loader import ConfigManager
from langchain.tools import Tool as LangchainTool
from typing import Dict, Type
from ..configs.loader import ConfigManager
from langchain.tools import tool
from langchain_community.tools import TavilySearchResults
from langchain import hub
from .tools.translator import TranslationTool
from langchain.agents import initialize_agent

class ToolRegistry:
    # """Registry of available tools"""
    _tools: Dict[str, Type[LangchainTool]] = {
        # Add more tools as needed
    }
    
    @classmethod
    def get_tool(cls, name: str) -> LangchainTool:
        if name not in cls._tools:
            raise ValueError(f"Tool '{name}' not found")
        return cls._tools[name]()

class AgentFactory:
    def __init__(self):
        self.config_manager = ConfigManager()


    @tool
    def magic_function(input: int) -> int:
        '''Applies a magic function to an input.'''
        return input + 2

    # tools = [magic_function]   

    def create_agent(self, config_name: str):
        """Create an agent from a configuration"""
        config = self.config_manager.load_config(config_name)
        
        # Initialize LLM with OpenAI functions
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106")

        
        # Initialize memory
        memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=5
        )
        
        # Initialize tools
        tools = []
        for tool_config in config.tools:
            if tool_config.enabled:
                try:
                    tool = ToolRegistry.get_tool(tool_config.name)
                    tools.append(tool)
                except ValueError as e:
                    print(f"Warning: {e}")

        translation_tool = TranslationTool()

        # Create the agent        
        tools = [translation_tool]


        # tools.append(self.magic_function)
        
        # prompt = ChatPromptTemplate.from_messages(
        #         [
        #             ("system", "You are a helpful assistant"),
        #             ("placeholder", "{chat_history}"),
        #             ("human", "{input}"),
        #             ("placeholder", "{agent_scratchpad}"),
        #         ]
        #     )
        # prompt = hub.pull("hwchase17/structured-chat-agent")


        translator_agent = initialize_agent(
            tools,
            llm,
            agent="zero-shot-react-description",
            verbose=True,
        )

        # Create agent with OpenAI functions
        return translator_agent

