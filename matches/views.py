from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from matches.models import Match, Map
from matches.serializers import (
    MatchSerializer,
    MatchCreateSerializer,
    MapSerializer,
)
from matches.services import create_match, get_match_state_at_round
from core.pagination import StandardResultsPagination
from core.permissions import IsOwnerOrAdmin


class MapListView(generics.ListAPIView):
    queryset = Map.objects.all()
    serializer_class = MapSerializer
    permission_classes = [permissions.IsAuthenticated]


class MatchListCreateView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get(self, request):
        matches = Match.objects.filter(user=request.user).select_related(
            "map", "stat"
        ).prefetch_related("rounds").order_by("-played_at")

        page = self.paginate_queryset(matches)
        serializer = MatchSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = MatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            match = create_match(
                user=request.user,
                validated_data=serializer.validated_data,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            MatchSerializer(match).data,
            status=status.HTTP_201_CREATED,
        )


class MatchDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = MatchSerializer

    def get_queryset(self):
        return Match.objects.filter(user=self.request.user).select_related(
            "map", "stat"
        ).prefetch_related("rounds")

    def get_object(self):
        match = get_object_or_404(
            Match.objects.select_related("map", "stat").prefetch_related("rounds"),
            pk=self.kwargs["pk"],
        )
        self.check_object_permissions(self.request, match)
        return match


class MatchStateAtRoundView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get(self, request, pk, round_n):
        match = get_object_or_404(Match, pk=pk)
        self.check_object_permissions(request, match)

        state = get_match_state_at_round(match, round_n)
        return Response(state)