from celery import shared_task
from django.db import transaction
from .models import Conversation
import re


@shared_task
def analyze_sentiment_task(conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return f"Conversation {conversation_id} not found."
    
    messages = conversation.messages.all()
    if not messages.exists():
        conversation.sentiment = "Neutral"
        conversation.save(update_fields=["sentiment"])
        return f"No messages in Conversation {conversation_id}. Set sentiment to Neutral."
    
    positive_words = re.compile(r"\b(happy|thank|thanks|great|solved|resolved|good|love|perfect|excellent|wonderful|appreciate|help)\b", re.IGNORECASE)
    negative_words = re.compile(r"\b(sad|angry|broken|worst|bad|refund|defect|fail|unhappy|disappointed|annoyed|terrible|frustrated|hate|error)\b", re.IGNORECASE)

    pos_count = 0
    neg_count = 0

    for message in messages:
        pos_count += len(positive_words.findall(message.content))
        neg_count += len(negative_words.findall(message.content))

    if pos_count > neg_count:
        sentiment = "Positive"
    elif neg_count > pos_count:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    with transaction.atomic():
        # Re-fetch or lock conversation to prevent race conditions
        conversation = Conversation.objects.select_for_update().get(
            id=conversation_id
        )
        conversation.sentiment = sentiment
        conversation.save(update_fields=['sentiment'])

    return f"Conversation {conversation_id} sentiment analyzed: {sentiment} (pos={pos_count}, neg={neg_count})"
