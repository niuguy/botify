from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from langchain_core.messages import HumanMessage
from botify.logging.logger import logger
from botify.agent.factory import AgentFactory


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process the user message using the selected agent."""
    logger.info(f"Processing message: {update.message.text}")
    # user_id = update.message.from_user.id

    # Check if an agent is selected
    current_agent = context.user_data.get("current_agent")
    if not current_agent:
        await update.message.reply_text(
            "Please select an agent first using /agents command"
        )
        return

    try:
        # Execute the agent's graph with the user's message
        result = current_agent.invoke(
            {"messages": [HumanMessage(content=update.message.text)]}
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
    # user_id = update.effective_user.id
    logger.info(f"Selected agent: {agent_name}")
    agent = AgentFactory.create(agent_name)
    # Store the selected agent type in user-specific context
    context.user_data["current_agent"] = agent

    # Initialize the agent for this user if not exists
    if "agent" not in context.user_data:
        # Note: You'll need to add LLM initialization here
        # agent = AgentFactory.create(agent_type, llm, **config)
        # context.user_data['agent'] = agent
        pass

    await query.edit_message_text(f"Selected agent: {agent_name}")
