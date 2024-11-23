from django.db import models
from django.contrib.auth.models import User

class Bot(models.Model):
    name = models.CharField(max_length=100)
    token = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Conversation(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    chat_id = models.CharField(max_length=100)
    user_message = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bot.name} - {self.chat_id}"
