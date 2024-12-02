import requests

def setup_webhook(bot_token: str, webhook_url: str) -> dict:
    """Set webhook URL for a bot"""
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    response = requests.post(api_url, json={'url': webhook_url})
    return response.json()

def get_webhook_info(bot_token: str) -> dict:
    """Get current webhook information"""
    api_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    response = requests.get(api_url)
    return response.json() 