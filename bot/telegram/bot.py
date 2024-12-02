import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import os
from .handlers import AgentCommandHandler
from langchain.agents import AgentExecutor
from langchain_community.tools import TavilySearchResults
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

class Bot:
    def __init__(self, token_env):
        self.token = os.getenv(token_env)
        self.application = Application.builder().token(self.token).build()
        #initialize agent command handler
        self.agent_command_handler = AgentCommandHandler()

    # Define a few command handlers. These usually take the two arguments update and
    # context.
    async def start(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}!",
            reply_markup=ForceReply(selective=True),
        )
        
    async def help_command(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        await update.message.reply_text("Help!")


    async def echo(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Echo the user message."""
        current_agent = context.user_data.get('current_agent')
        if current_agent:
            # tools = [TavilySearchResults(max_results=1)]
            # agent_executor = AgentExecutor(agent=context.user_data['current_agent'],tools=tools,verbose=False)
            # await agent_executor.invoke({"input": update.message.text})
            input_text = "Hello, how are you?;English;French"
            response = current_agent.run(input_text)
            await update.message.reply_text(response)

        else:
            await update.message.reply_text("No active agent. Use /switch_agent to select one.")

    def run(self) -> None:
        """Start the bot."""
        # on different commands - answer in Telegram
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("agents", self.agent_command_handler.list_agents))
        self.application.add_handler(CommandHandler("switch_agent", self.agent_command_handler.switch_agent))
        self.application.add_handler(CallbackQueryHandler(self.agent_command_handler.handle_callback_query))

        # on non command i.e message - echo the message on Telegram
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))

        # Run the bot until the user presses Ctrl-C
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
