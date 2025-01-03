from botify.agent.agent_factory import AgentFactory


def test_rag_agent(capsys):
    workflow = AgentFactory.create(
        "reader", url="https://www.example.com"
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
