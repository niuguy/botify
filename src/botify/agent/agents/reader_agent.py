from typing import Annotated, Sequence, Literal, List
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from botify.logging.logger import logger
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain import hub
from langgraph.graph import Graph, StateGraph, START, END
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableConfig
import tempfile
import shutil
from langchain.tools.retriever import create_retriever_tool
from botify.scraper.scraper import Scraper
from botify.agent.agents.base_agent import BaseAgent


class RagAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


class ReaderAgent(BaseAgent):
    """Agent that handles RAG (Retrieval Augmented Generation) operations."""

    def __init__(self, llm: ChatOpenAI, url: str):
        # Initialize LLM models
        self.chat_model = ChatOpenAI(temperature=0, model="gpt-4-turbo")
        self.grading_model = ChatOpenAI(
            temperature=0, model="gpt-4-0125-preview", streaming=True
        )
        self.generation_model = ChatOpenAI(
            model_name="gpt-3.5-turbo", temperature=0, streaming=True
        )

        # Initialize components for later use
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=100, chunk_overlap=50
        )

        # Initialize as None
        self.vectorstore = None
        self.retriever = None
        self.persist_dir = None
        self.retriever_tool = None
        self.chat_model_with_tools = None
        print(f"Debug - URL: {url}")
        if url:
            documents = self.scrape_url(url)
            self.set_context_documents(documents)
        self.flow = self.generate_flow()

    def scrape_url(self, url: str) -> List[Document]:
        """Scrape the url and return the documents."""
        logger.info(f"Scraping URL: {url}")
        print(f"Debug - Scraping URL: {url}")
        scraper = Scraper([url])

        documents = scraper.run()
        return documents

    def set_context_documents(self, documents: List[Document]) -> None:
        """Sets new documents as the context for the next interaction.
        Creates a new vector store for each request.

        Args:
            documents: List of Document objects to use as context
        """
        # Cleanup previous temporary directory if it exists
        if self.persist_dir:
            try:
                shutil.rmtree(self.persist_dir)
            except Exception as e:
                logger.warning(f"Failed to cleanup temporary directory: {e}")

        # Create new temporary directory
        self.persist_dir = tempfile.mkdtemp()

        # Create new vector store
        self.vectorstore = Chroma(
            collection_name="rag-chroma",
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir,
        )

        # Split and add new documents
        doc_splits = self.text_splitter.split_documents(documents)
        self.vectorstore.add_documents(doc_splits)
        logger.info(f"Added {len(doc_splits)} new document chunks to the vector store")

        # Update retriever and tools
        self.retriever = self.vectorstore.as_retriever()

        # Create new retriever tool
        self.retriever_tool = create_retriever_tool(
            self.retriever,
            name="retrieve_web_content",
            description="Search and return information about web content",
        )

        # Bind the new tool to the chat model
        self.chat_model_with_tools = self.chat_model.bind_tools([self.retriever_tool])

    def __del__(self):
        """Cleanup temporary directory when the agent is destroyed."""
        if self.persist_dir:
            try:
                shutil.rmtree(self.persist_dir)
            except Exception as e:
                logger.warning(f"Failed to cleanup temporary directory: {e}")

    def agent(self, state):
        """Invokes the agent model to generate a response."""
        print("---CALL AGENT---")
        if not self.chat_model_with_tools:
            raise ValueError(
                "No documents have been set. Call set_context_documents first."
            )
        messages = state["messages"]
        response = self.chat_model_with_tools.invoke(messages)
        return {"messages": [response]}

    def rewrite(self, state):
        """Transform the query to produce a better question."""
        print("---TRANSFORM QUERY---")
        messages = state["messages"]
        question = messages[0].content

        msg = [
            HumanMessage(
                content=f""" \n 
        Look at the input and try to reason about the underlying semantic intent / meaning. \n 
        Here is the initial question:
        \n ------- \n
        {question} 
        \n ------- \n
        Formulate an improved question: """,
            )
        ]

        response = self.grading_model.invoke(msg)
        return {"messages": [response]}

    def grade_documents(self, state) -> Literal["generate", "rewrite"]:
        """
        Determines whether the retrieved documents are relevant to the question.

        Args:
            state (messages): The current state

        Returns:
            str: A decision for whether the documents are relevant or not
        """

        print("---CHECK RELEVANCE---")

        # Data model
        class grade(BaseModel):
            """Binary score for relevance check."""

            binary_score: str = Field(description="Relevance score 'yes' or 'no'")

        # LLM
        model = ChatOpenAI(temperature=0, model="gpt-4-0125-preview", streaming=True)

        # LLM with tool and validation
        llm_with_tool = model.with_structured_output(grade)

        # Prompt
        prompt = PromptTemplate(
            template="""You are a grader assessing relevance of a retrieved document to a user question. \n 
            Here is the retrieved document: \n\n {context} \n\n
            Here is the user question: {question} \n
            If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.""",
            input_variables=["context", "question"],
        )

        # Chain
        chain = prompt | llm_with_tool

        messages = state["messages"]
        last_message = messages[-1]

        question = messages[0].content
        docs = last_message.content

        scored_result = chain.invoke({"question": question, "context": docs})

        score = scored_result.binary_score

        if score == "yes":
            print("---DECISION: DOCS RELEVANT---")
            return "generate"

        else:
            print("---DECISION: DOCS NOT RELEVANT---")
            print(score)
            return "rewrite"

    def generate(self, state):
        """
        Generate answer

        Args:
            state (messages): The current state

        Returns:
            dict: The updated state with re-phrased question
        """
        print("---GENERATE---")
        messages = state["messages"]
        question = messages[0].content
        last_message = messages[-1]

        docs = last_message.content

        # Prompt
        prompt = hub.pull("rlm/rag-prompt")

        # LLM
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, streaming=True)

        # Post-processing
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # Chain
        rag_chain = prompt | llm | StrOutputParser()

        # Run
        response = rag_chain.invoke({"context": docs, "question": question})
        return {"messages": [response]}

    def generate_flow(self) -> Graph:
        workflow = StateGraph(RagAgentState)

        # Define the nodes we will cycle between
        workflow.add_node("agent", self.agent)  # Agent decision node
        workflow.add_node("retrieve", ToolNode([self.retriever_tool]))  # Retrieval node
        workflow.add_node("rewrite", self.rewrite)  # Query rewriting node
        workflow.add_node("generate", self.generate)  # Response generation node

        # Initial edge: Start -> Agent
        workflow.add_edge(START, "agent")

        # Agent decision edges
        workflow.add_conditional_edges(
            "agent",
            tools_condition,
            {
                "tools": "retrieve",  # If tools needed, go to retrieve
                END: END,  # If no tools needed, end
            },
        )

        # Retrieval result edges
        workflow.add_conditional_edges(
            "retrieve",
            self.grade_documents,
            {
                "generate": "generate",  # If documents relevant, generate response
                "rewrite": "rewrite",  # If documents not relevant, rewrite query
            },
        )

        # Final edges
        workflow.add_edge("generate", END)  # Generation complete -> End
        workflow.add_edge("rewrite", "agent")  # After rewrite -> Back to agent

        return workflow.compile()

    def run(self, inputs: dict, config: RunnableConfig):
        # set context documents
        return self.flow.invoke(inputs, config)
