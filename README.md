# Botify

A telegram bot framework for building AI agents. built with langgraph and langchain.


## Installation

```bash
make install
```

## Configuration

You will need to get a telegram bot token from [@BotFather](https://t.me/botfather) and set it as an environment variable `TELE_BOT_TOKEN`.

## Run the bot

```bash
make run
```
## Use the bot


On telegram, input /agents to see the list of available agents. 

Currently available agents:

1. **Chat Agent**: A basic conversational agent that can engage in general dialogue and use tools like weather information and web search.

2. **Reader Agent**: A RAG (Retrieval Augmented Generation) agent that can:
   - Process and understand web content from provided URLs
   - Answer questions about the content using vector search
   - Provide contextual responses based on the loaded documents

## Add new agent

To add a new agent, create a new file in the `src/botify/agent/agents` directory. The file should contain a class that inherits from `BaseAgent`. 