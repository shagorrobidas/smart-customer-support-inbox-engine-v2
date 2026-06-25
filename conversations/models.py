from django.db import models
from core.models import BaseModel


class Conversation(BaseModel):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('resolved', 'Resolved'),
        ('snoozed', 'Snoozed'),
    ]
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]

    customer_name = models.CharField(
        max_length=255,
        db_index=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='open'
    )
    sentiment = models.CharField(
        max_length=10,
        choices=SENTIMENT_CHOICES,
        default='neutral'
    )

    def __str__(self):
        return f"Conversation with {self.customer_name} - Status: {self.status}, Sentiment: {self.sentiment}"  # noqa: E501

    @property
    def last_message(self):
        last_msg = self.messages.order_by('-timestamp').first()
        return last_msg.message if last_msg else "No messages yet"


class Message(BaseModel):
    SENDER_CHOICES = [
        ('customer', 'Customer'),
        ('agent', 'Agent'),
    ]

    conversation = models.ForeignKey(
        Conversation,
        related_name='messages',
        on_delete=models.CASCADE
    )
    sender = models.CharField(
        max_length=10,
        choices=SENDER_CHOICES
    )
    message = models.TextField()
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        return f"Message {self.id} from {self.sender} in Conversation {self.conversation.id}"   # noqa
