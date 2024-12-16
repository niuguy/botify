from botify.agent.agent_factory import AgentFactory, AgentType


def test_rag_agent(capsys):
    workflow = AgentFactory.create(
        AgentType.READER.value, url="https://www.example.com"
    )

    result = workflow.run(
        {
            "messages": [
                ("user", "What this domain is used for?"),
            ]
        },
        config={},
    )

    print(result)
