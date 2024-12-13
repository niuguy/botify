from langchain_core.tools import tool
from botify.logging.logger import logger
from langgraph.prebuilt import ToolNode
from langchain_community.tools import TavilySearchResults
# from botify.agent.rag import retriever

"""
https://python.langchain.com/docs/integrations/tools/

"""


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


search_tool = TavilySearchResults(max_results=5, search_depth="advanced")

# retriever_tool = create_retriever_tool(
#     retriever,
#     "retrieve_blog_posts",
#     "Search and return information about Lilian Weng blog posts on LLM agents, prompt engineering, and adversarial attacks on LLMs.",
# )
# retriever_tools = [retriever_tool]
# retriever_tool_node = ToolNode([retriever_tool])

tools = [search_tool]
tool_node = ToolNode(tools)
