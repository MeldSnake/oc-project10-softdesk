# Create your views here.
from rest_framework.viewsets import ModelViewSet
from .serializers import ProjectSerializer, ProjectCreateSerializer
from .models import User, Contributor, Project
from django.db import transaction
from django.db.models import Q


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @transaction.atomic()
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            Q(contributors__user=self.request.user)
            | Q(author=self.request.user))
        return queryset
