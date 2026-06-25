from rest_framework import serializers
from conversations.models import (
    Conversation,
    Message
)
from conversations.utils import get_conversation_lock


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'message',
            'timestamp'
        ]
        read_only_fields = [
            'id',
            'sender',
            'timestamp'
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        conversation = self.context.get('conversation')

        if request and conversation:
            user = request.user
            lock = get_conversation_lock(conversation.id)

            # If the conversation is locked by another agent, block execution
            if lock['is_locked'] and lock['locked_by_id'] != user.id:
                raise serializers.ValidationError(
                    f"This conversation is locked by another agent ({lock['locked_by_email']}). "
                    "You cannot submit messages until the lock is released or expires."
                )
        return attrs


class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.CharField(read_only=True)
    lock_info = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id',
            'customer_name',
            'last_message',
            'status',
            'sentiment',
            'created_at',
            'lock_info'
        ]
        read_only_fields = [
            'id',
            'last_message',
            'sentiment',
            'created_at'
        ]

    def get_lock_info(self, obj):
        return get_conversation_lock(obj.id)
