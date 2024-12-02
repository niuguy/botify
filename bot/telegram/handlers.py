# apps/telegram_bot/handlers.py
import uuid
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from ..configs.loader import ConfigManager
from ..agents.factory import AgentFactory

class AgentCommandHandler:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.agent_factory = AgentFactory()
    
    async def list_agents(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List available agent configurations"""
        configs = self.config_manager.list_configs()
        print(configs)
        
        keyboard = []
        for config_name in configs:
            config = self.config_manager.load_config(config_name)
            keyboard.append([
                InlineKeyboardButton(
                    f"🤖 {config.name} - {config.description[:30]}...",
                    callback_data=f"switch_agent_{config.name}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Choose an agent type:",
            reply_markup=reply_markup
        )
    
    async def switch_agent(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Switch to a different agent"""
        print("switching agent to ", update.callback_query.data)
        query = update.callback_query
        config_name = query.data.replace("switch_agent_", "")
        
        # Create new agent
        agent = self.agent_factory.create_agent(config_name)
        context.user_data['current_agent'] = agent
        config = self.config_manager.load_config(config_name)
        
        # Store in context
        if 'conversations' not in context.user_data:
            context.user_data['conversations'] = {}
        
        # Create new conversation with this agent
        conv_id = str(uuid.uuid4())
        context.user_data['conversations'][conv_id] = {
            'agent': agent,
            'config': config_name,
            'created_at': datetime.now()
        }
        context.user_data['active_conversation'] = conv_id
        
        await query.edit_message_text(
            f"Switched to {config.name}!\n\n"
            f"This agent is configured to: {config.description}\n\n"
            "You can start chatting now!"
        )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline buttons"""
        query = update.callback_query
        if query.data.startswith("switch_agent_"):
            await self.switch_agent(update, context)