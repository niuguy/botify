from telegram import Update, ForceReply
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from gpt_researcher import GPTResearcher
import logging

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message

Send any text message to start a research query.
The bot will analyze your query and provide a detailed research report.
    """
    await update.message.reply_text(help_text)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and conduct research."""
    query = update.message.text
    
    # Optional: Acknowledge receipt of query
    await update.message.reply_text("Starting research on your query. This may take a few minutes...")
    
    try:
        # Initialize researcher and conduct research
        researcher = GPTResearcher(query)
        research_result = await researcher.conduct_research()
        
        # Optional: Show typing indicator while preparing report
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )
        
        # Generate and send report
        report = await researcher.write_report()
        
        # Split report into chunks if it's too long
        chunk_size = 4096  # Telegram's message size limit
        report_chunks = [report[i:i + chunk_size] for i in range(0, len(report), chunk_size)]
        
        # Send each chunk separately
        for chunk in report_chunks:
            await update.message.reply_text(chunk)
            
    except Exception as e:
        logger.error(f"Error processing research query: {str(e)}")
        await update.message.reply_text(
            "Sorry, an error occurred while processing your research query. Please try again later."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Error occurred: {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Sorry, an error occurred while processing your request. Please try again later."
            )
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}")
