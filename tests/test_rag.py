from botify.agent.agent_factory import AgentFactory
from langchain_openai import ChatOpenAI
import pprint


def test_rag_agent(capsys):
    llm = ChatOpenAI(model="gpt-4-mini", temperature=0, streaming=True)
    workflow = AgentFactory.create_rag_agent(llm=llm)

    inputs = {
        "messages": [
            ("user", "What does Lilian Weng say about the types of agent memory?"),
        ]
    }
    for output in workflow.invoke(inputs):
        with capsys.disabled():
            for key, value in output.items():
                pprint.pprint(f"Output from node '{key}':")
                pprint.pprint("---")
                pprint.pprint(value, indent=2, width=80, depth=None)
            pprint.pprint("\n---\n")
