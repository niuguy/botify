from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from langchain_core.messages import HumanMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from botify.logging.logger import logger
from botify.agent.agent_factory import AgentFactory
import uuid

chats_by_session_id = {}

# Define states
WAITING_FOR_URL = 1


def get_chat_history(session_id: str) -> InMemoryChatMessageHistory:
    chat_history = chats_by_session_id.get(session_id)
    if chat_history is None:
        chat_history = InMemoryChatMessageHistory()
        chats_by_session_id[session_id] = chat_history
    return chat_history


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process the user message using the selected agent."""
    logger.info(f"Processing message: {update.message.text}")

    # Check if we're waiting for a URL
    if context.user_data.get("waiting_for_url"):
        url = update.message.text
        session_id = str(uuid.uuid4())

        try:
            # Create RAG agent with the provided URL
            agent = AgentFactory.create("reader", url=url)
            context.user_data["current_agent"] = agent
            context.user_data["session_id"] = session_id
            context.user_data["waiting_for_url"] = False  # Reset the waiting state

            await update.message.reply_text(f"Reader agent created with URL: {url}")
            return
        except Exception as e:
            logger.error(f"Error creating reader agent: {str(e)}")
            await update.message.reply_text(
                "Invalid URL or error creating reader agent. Please try again."
            )
            return

    # Check if an agent is selected
    current_agent = context.user_data.get("current_agent")
    session_id = context.user_data.get("session_id")

    if not current_agent:
        await update.message.reply_text(
            "Please select an agent first using /agents command"
        )
        return

    try:
        # Execute the agent's graph with the user's message
        logger.info(f"Invoking agent: {current_agent}")
        result = current_agent.run(
            {"messages": [HumanMessage(content=update.message.text)]},
            config={"configurable": {"session_id": session_id}},
        )
        logger.info(f"Agent result: {result}")
        await update.message.reply_text(result["messages"][-1].content)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        await update.message.reply_text(
            "Sorry, there was an error processing your message."
        )


async def agents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /agents command - show available agents and allow selection."""
    # user_id = update.effective_user.id

    # Get available agent types from AgentFactory
    available_agents = AgentFactory.get_agent_list()

    # Create keyboard with available agents
    keyboard = [
        [InlineKeyboardButton(agent_type, callback_data=f"select_agent:{agent_type}")]
        for agent_type in available_agents
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Show current agent if exists
    current_agent = context.user_data.get("current_agent", "None")
    message = f"Current agent: {current_agent}\n" "Available agents:"

    await update.message.reply_text(message, reply_markup=reply_markup)


async def agent_selection_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle agent selection from inline keyboard."""
    query = update.callback_query
    await query.answer()

    # Extract agent type from callback data
    agent_name = query.data.split(":")[1]
    logger.info(f"Selected agent: {agent_name}")

    if agent_name == "reader":
        # Set state to wait for URL
        context.user_data["waiting_for_url"] = True
        await query.edit_message_text("Please send the web URL you want to read")
        return

    session_id = str(uuid.uuid4())

    agent = AgentFactory.create(agent_name)
    # Store the selected agent type in user-specific context
    context.user_data["current_agent"] = agent
    context.user_data["session_id"] = session_id

    # Initialize the agent for this user if not exists
    if "agent" not in context.user_data:
        # Note: You'll need to add LLM initialization here
        # agent = AgentFactory.create(agent_type, llm, **config)
        # context.user_data['agent'] = agent
        pass

    await query.edit_message_text(f"Selected agent: {agent_name}")
