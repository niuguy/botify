from botify.agent.agent_factory import AgentFactory


def test_researcher_agent(capsys):
    workflow = AgentFactory.create("researcher")

    result = workflow.run(
        {
            "messages": [
                "iwoca",
            ]
        },
        config={},
    )

    print(result)
