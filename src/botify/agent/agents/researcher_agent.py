from typing import TypedDict, List, Dict, Any
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from langgraph.graph import Graph, StateGraph
from langchain_core.runnables import RunnablePassthrough
from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain_core.runnables import RunnableConfig
from .base_agent import BaseAgent
from botify.logging.logger import logger
from langchain_core.messages import BaseMessage

class ResearcherAgentState(TypedDict):
    messages: List[BaseMessage]
    search_results: List[Dict[str, Any]]
    reference_docs: List[Document]
    outline: str
    sections: List[Dict[str, str]]
    final_report: str

search_tool = TavilySearchResults(max_results=2)



class ResearcherAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm)
        self.llm = ChatOpenAI(model="gpt-4-turbo")
        self.outline_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a research assistant. Create a detailed outline for a research report 
            based on the given query. The outline should be comprehensive and well-structured."""),
            ("user", "Query: {query}\n\nAvailable references:\n{references}")
        ])
        self.section_prompt = ChatPromptTemplate.from_messages([
            ("system", """Write a detailed section for a research report based on the provided outline 
            section and reference materials. Include in-text citations using [Author] or [Source] format."""),
            ("user", """Section to write: {section}
            
            Available references:
            {references}
            
            Write a detailed, well-researched section:""")
        ])
        self.compile_prompt = ChatPromptTemplate.from_messages([
            ("system", """Compile the provided sections into a cohesive research report. 
            Ensure smooth transitions between sections and maintain consistent formatting. 
            Include a references section at the end."""),
            ("user", "Sections:\n{sections}\n\nReferences:\n{references}")
        ])


    # Search function
    def search_for_info(self, state: ResearcherAgentState) -> ResearcherAgentState:
        """Perform search based on query and store results"""
        query = state["messages"][-1]
        results = search_tool.invoke(query)
        state["search_results"] = results
        return state

    # Process search results into reference documents
    async def fetch_url_content(self, session: aiohttp.ClientSession, url: str) -> Dict[str, str]:
        """Fetch and parse content from a URL"""
        print("fetching url", url)
        try:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text content
                    text = soup.get_text(separator=' ', strip=True)
                    
                    # Basic text cleaning
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    text = ' '.join(lines)
                    
                    return {
                        "url": url,
                        "content": text[:10000],  # Limit content length
                        "status": "success"
                    }
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return {"url": url, "content": "", "status": "error"}
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return {"url": url, "content": "", "status": "error"}
    
    async def crawl_urls(self, urls: List[str]) -> List[Dict[str, str]]:
        """Crawl multiple URLs concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_url_content(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
            return results

    def process_references(self, state: ResearcherAgentState) -> ResearcherAgentState:
        """Convert search results into structured reference documents with full content"""
        # Extract URLs from search results
        print("search_results", state["search_results"])
        urls = [result["url"] for result in state["search_results"]]
        
        # Run async crawling in a thread pool
        with ThreadPoolExecutor() as executor:
            loop = asyncio.new_event_loop()
            crawled_contents = loop.run_until_complete(self.crawl_urls(urls))
            loop.close()
        
        # Create documents with both snippet and full content
        docs = []
        for result, crawled in zip(state["search_results"], crawled_contents):
            full_content = crawled["content"] if crawled["status"] == "success" else result["content"]
            title = result.get("title", "") if result.get("title", "") else result.get("url", "")
            doc = Document(
                page_content=full_content,
                metadata={
                    "title": title,
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "source": "Google Search",
                    "crawl_status": crawled["status"]
                }
            )
            docs.append(doc)
        
        state["reference_docs"] = docs
        return state
    
    # Generate outline
    def create_outline(self, state: ResearcherAgentState) -> ResearcherAgentState:
        """Generate report outline based on query and references"""
        references_text = "\n".join([
            f"- {doc.metadata['title']}: {doc.page_content}"
            for doc in state["reference_docs"]
        ])
        
        outline_prompt_value = self.outline_prompt.invoke({
            "query": state["messages"][-1],
            "references": references_text
        })

        print("outline_prompt_value", outline_prompt_value) 

        
        state["outline"] = self.llm.invoke(outline_prompt_value).content
        return state
    
    def write_sections(self, state: ResearcherAgentState) -> ResearcherAgentState:
        """Write individual sections based on outline and references"""
        # Parse outline into sections
        sections = [s.strip() for s in state["outline"].split("\n") if s.strip()]
        
        written_sections = []
        references_text = "\n".join([
            f"- {doc.metadata['title']}: {doc.page_content}"
            for doc in state["reference_docs"]
        ])

        print("sections", sections)
        
        for section in sections:
            print("processing section", section)
            # Get the section content from the LLM
            section_prompt_value = self.section_prompt.invoke({
                "section": section,
                "references": references_text
            })
            section_content = self.llm.invoke(section_prompt_value).content
            
            written_sections.append({
                "heading": section,
                "content": section_content
            })
        
        state["sections"] = written_sections  # Store the list of sections directly
        return state
    
    def compile_report(self, state: ResearcherAgentState) -> ResearcherAgentState:
        """Compile all sections into final report with references"""
        sections_text = "\n\n".join([
            f"# {section['heading']}\n{section['content']}"
            for section in state["sections"]
        ])
        
        references_text = "\n".join([
            f"- {doc.metadata['title']}: {doc.metadata['link']}"
            for doc in state["reference_docs"]
        ])
        
        final_report = self.compile_prompt.invoke({
            "sections": sections_text,
            "references": references_text
        })
        
        state["final_report"] = self.llm.invoke(final_report).content
        return state


    def generate_flow(self) -> Graph:
        """Create and configure the research workflow graph"""
        workflow = StateGraph(ResearcherAgentState)
        
        # Add nodes
        workflow.add_node("search", self.search_for_info)
        workflow.add_node("process_refs", self.process_references)
        workflow.add_node("create_outline", self.create_outline)
        workflow.add_node("write_sections", self.write_sections)
        workflow.add_node("compile_report", self.compile_report)
        
        # Define edges
        workflow.add_edge("search", "process_refs")
        workflow.add_edge("process_refs", "create_outline")
        workflow.add_edge("create_outline", "write_sections")
        workflow.add_edge("write_sections", "compile_report")
        
        # Set entry and exit points
        workflow.set_entry_point("search")
        workflow.set_finish_point("compile_report")
        
        return workflow.compile()

    def run(self, inputs: dict, config: RunnableConfig):
        return self.generate_flow().invoke(inputs, config)


