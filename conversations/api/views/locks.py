from rest_framework import generics, permissions, status
from conversations.models import Conversation

from conversations.utils import (
    get_conversation_lock,
    acquire_conversation_lock,
    release_conversation_lock
)

from api.utils import (
    CustomResponse,
)


class ConversationLockView(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]
    queryset = Conversation.objects.all()

    def post(self, request, pk):
        conversation = self.get_object()
        user = request.user

        acquired = acquire_conversation_lock(conversation.id, user.id)
        lock_state = get_conversation_lock(conversation.id)
        if acquired:
            return CustomResponse.success(
                message="Lock acquired successfully.",
                data={"lock_info": lock_state},
                status_code=status.HTTP_200_OK
            )
        else:
            return CustomResponse.error(
                message="This conversation is currently locked by another agent.",
                status_code=status.HTTP_409_CONFLICT,
                data={"lock_info": lock_state}
            )


class ConversationUnlockView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Conversation.objects.all()

    def post(self, request, pk):
        conversation = self.get_object()
        user = request.user
        released = release_conversation_lock(conversation.id, user.id)

        if released:
            return CustomResponse.success(
                message="Lock released successfully.",
                status_code=status.HTTP_200_OK
            )
        else:
            lock_state = get_conversation_lock(conversation.id)
            return CustomResponse.error(
                message="You do not own the lock for this conversation and cannot release it.",
                status_code=status.HTTP_403_FORBIDDEN,
                data={"lock_info": lock_state}
            )
