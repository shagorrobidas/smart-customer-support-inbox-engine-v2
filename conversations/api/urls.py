from django.urls import path
from conversations.api.views import (
    ConversationListView,
    ConversationDetailView,
    ConversationMessagesView,
    ConversationSuggestReplyView,
    ConversationLockView,
    ConversationUnlockView,
)

urlpatterns = [
    path(
        '',
        ConversationListView.as_view(),
        name='conversation-list'
    ),
    path(
        '<int:pk>/',
        ConversationDetailView.as_view(),
        name='conversation-detail'
    ),
    path(
        '<int:pk>/messages/',
        ConversationMessagesView.as_view(),
        name='conversation-messages'
    ),
    path(
        '<int:pk>/suggest-reply/',
        ConversationSuggestReplyView.as_view(),
        name='conversation-suggest-reply'
    ),
    path(
        '<int:pk>/lock/',
        ConversationLockView.as_view(),
        name='conversation-lock'
    ),
    path(
        '<int:pk>/unlock/',
        ConversationUnlockView.as_view(),
        name='conversation-unlock'
    ),
]