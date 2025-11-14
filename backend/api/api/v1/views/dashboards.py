from rest_framework.generics import ListAPIView

from .... import models
from ....serializers import DashboardSnapshotSerializer, NewsMentionSerializer


class DashboardSnapshotView(ListAPIView):
    serializer_class = DashboardSnapshotSerializer

    def get_queryset(self):
        slug = self.request.query_params.get("slug")
        queryset = models.DashboardSnapshot.objects.all()
        if slug:
            queryset = queryset.filter(slug=slug)
        date = self.request.query_params.get("date")
        if date:
            queryset = queryset.filter(date=date)
        return queryset.order_by("-date")


class NewsMentionsView(ListAPIView):
    serializer_class = NewsMentionSerializer

    def get_queryset(self):
        query = self.request.query_params.get("query")
        queryset = models.NewsMention.objects.all()
        if query:
            queryset = queryset.filter(query=query)
        return queryset.order_by("-published_at")

