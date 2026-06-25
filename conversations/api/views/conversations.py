from rest_framework import generics, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.shortcuts import get_object_or_404
from conversations.models import Conversation, Message
from conversations.api.serializers import (
    ConversationSerializer,
    MessageSerializer
)

from conversations.consumers import broadcast_message
from conversations.services.ai import AISuggetionsService
from conversations.tasks import analyze_sentiment_task
from api.utils import (
    CustomResponse,
    CustomPagination,
)


class ConversationListView(generics.ListCreateAPIView):
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['status']
    search_fields = ['customer_name']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            message="Conversations retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        initial_message_text = request.data.get('message')

        conversation = serializer.save()

        if initial_message_text:
            Message.objects.create(
                conversation=conversation,
                sender='customer',
                message=initial_message_text
            )

            serializer = self.get_serializer(conversation)

        return CustomResponse.success(
            message="Conversation started successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )


class ConversationDetailView(generics.RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(
            message="Conversation details retrieved successfully..",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class ConversationMessagesView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        conversation_id = self.kwargs['pk']
        return Message.objects.filter(
            conversation_id=conversation_id
        ).order_by('-timestamp')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['conversation'] = get_object_or_404(Conversation, id=self.kwargs['pk'])
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return CustomResponse.success(
            message="Agent reply sent successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        conversation = get_object_or_404(Conversation, id=self.kwargs['pk'])

        serializer.save(conversation=conversation, sender='agent')

        analyze_sentiment_task.delay(conversation.id)

        broadcast_message(conversation.id, serializer.data)


class ConversationSuggestReplyView(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]
    queryset = Conversation.objects.all()

    def post(self, request, pk):
        message_text = request.data.get('message', '')

        if not message_text:
            return CustomResponse.error(
                message="The 'message' field is required in the request body.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        suggestion = AISuggetionsService.suggest_reply(message_text)
        return CustomResponse.success(
            message="AI reply suggestion generated successfully.",
            data={"suggestion": suggestion},
            status_code=status.HTTP_200_OK
        )
