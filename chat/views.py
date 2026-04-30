from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from accounts.services import are_friends
from .services import get_conversation
from .serializers import ChatMessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatHistory(APIView):
    
    def get(self, request, recepient_id):
        user = self.request.user
        recepient = get_object_or_404(User,id=recepient_id)
        friends = are_friends(user, recepient)

        if not friends:
            return Response(status=status.HTTP_403_FORBIDDEN)

        chat_history = get_conversation(user, recepient)
        serializer = ChatMessageSerializer(chat_history, many=True)
        return Response(serializer.data)

            