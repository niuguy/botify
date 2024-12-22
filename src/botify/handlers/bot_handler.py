# src/botify/handlers/base.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from botify.services.agent_service import AgentService
from botify.logging.logger import logger


class BotHandler:
    def __init__(self):
        self.agent_service = AgentService()

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process the user message using the selected agent."""
        try:
            if context.user_data.get("waiting_for_url"):
                await self._handle_url_input(update, context)
                return

            session_id = context.user_data.get("session_id")
            if not session_id:
                await update.message.reply_text(
                    "Please select an agent first using /agents command"
                )
                return

            response = await self.agent_service.process_message(
                update.message.text, session_id
            )
            await update.message.reply_text(response)

        except Exception as e:
            logger.error(f"Error in echo handler: {str(e)}")
            await update.message.reply_text(
                "Sorry, there was an error processing your message."
            )

    async def _handle_url_input(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle URL input for reader agent"""
        url = update.message.text
        try:
            session = self.agent_service.create_reader_agent(url)
            context.user_data.update(
                {"session_id": session.session_id, "waiting_for_url": False}
            )
            await update.message.reply_text(f"Reader agent created with URL: {url}")
        except Exception:
            await update.message.reply_text(
                "Invalid URL or error creating reader agent. Please try again."
            )

    async def post_init(self, application) -> None:
        available_agents = self.agent_service.get_available_agents()
        commands =[(agent_name,"") for agent_name in available_agents]
        await application.bot.set_my_commands(commands)

    async def agents(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /agents command"""
        available_agents = self.agent_service.get_available_agents()

        keyboard = [
            [
                InlineKeyboardButton(
                    agent_type, callback_data=f"select_agent:{agent_type}"
                )
            ]
            for agent_type in available_agents
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        current_agent = context.user_data.get("current_agent", "None")
        message = f"Current agent: {current_agent}\nAvailable agents:"

        await update.message.reply_text(message, reply_markup=reply_markup)

    async def agent_selection_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle agent selection from inline keyboard."""
        query = update.callback_query
        await query.answer()

        agent_name = query.data.split(":")[1]

        if agent_name == "reader":
            context.user_data["waiting_for_url"] = True
            await query.edit_message_text("Please send the web URL you want to read")
            return

        try:
            session = self.agent_service.create_agent(agent_name)
            context.user_data["session_id"] = session.session_id
            await query.edit_message_text(f"Selected agent: {agent_name}")
        except Exception as e:
            await query.edit_message_text(f"Error selecting agent: {str(e)}")
