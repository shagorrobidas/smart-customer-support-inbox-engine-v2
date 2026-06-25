from django.contrib import admin
from conversations.models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer_name',
        'status',
        'sentiment',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'status',
        'sentiment',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'customer_name',
    )
    ordering = (
        '-created_at',
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'conversation',
        'sender',
        'timestamp',
    )
    list_filter = (
        'sender',
        'timestamp',
    )
    search_fields = (
        'conversation__customer_name',
        'message',
    )
    ordering = (
        '-timestamp',
    )