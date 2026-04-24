from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from accounts.models import User, FriendRequest
from django.db.models import Q
from accounts.serializers import (
    UserSerializer,
    PublicUserSerializer,
    FriendRequestSerializer,
)
from accounts.services import (
    send_friend_request,
    respond_to_friend_request,
    are_friends,
)
from core.permissions import IsOwnerOrAdmin


class OwnProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class PublicProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PublicUserSerializer
    queryset = User.objects.all()


class FriendRequestListCreateView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        received = FriendRequest.objects.filter(
            receiver=request.user,
            status=FriendRequest.Status.PENDING,
        ).select_related("sender")
        serializer = FriendRequestSerializer(received, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FriendRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            fr = send_friend_request(
                sender=request.user,
                receiver=serializer.validated_data["receiver"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            FriendRequestSerializer(fr).data,
            status=status.HTTP_201_CREATED,
        )


class FriendRequestRespondView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        fr = get_object_or_404(
            FriendRequest,
            pk=pk,
            receiver=request.user,
        )

        accepting = request.data.get("accepting")
        if accepting is None:
            return Response(
                {"detail": "Field 'accepting' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            fr = respond_to_friend_request(fr, accepting=bool(accepting))
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(FriendRequestSerializer(fr).data)
    

class FriendsListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PublicUserSerializer

    def get_queryset(self):
        user = self.request.user
        accepted = FriendRequest.objects.filter(
            Q(sender=user) | Q(receiver=user),
            status=FriendRequest.Status.ACCEPTED,
        ).values_list("sender_id", "receiver_id")

        friend_ids = set()
        for sender_id, receiver_id in accepted:
            friend_ids.add(sender_id if sender_id != user.id else receiver_id)

        return User.objects.filter(id__in=friend_ids)