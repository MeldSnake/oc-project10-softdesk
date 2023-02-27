# Create your views here.
from rest_framework import mixins, generics, views
from .serializers import (ProjectSerializer,
                          ContributorSerializer,
                          IssueSerializer)
from .models import (Contributor, Project, Issue, User)
from django.db.models import Q
from rest_framework import authentication, permissions
from django.shortcuts import get_object_or_404
from rest_framework import (response, status)


class ProjectAPIViewMixin:
    queryset = Project.objects.prefetch_related('contributors', 'author')
    serializer_class = ProjectSerializer
    lookup_url_kwarg = "project_id"
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset.filter(
            Q(author=self.request.user)
            | Q(contributors__user=self.request.user)
        )
        return queryset


class ProjectsAPIView(ProjectAPIViewMixin,
                     generics.ListCreateAPIView):
    def get_view_name(self) -> str:
        return "Projects"


class ProjectIndexedAPIView(ProjectAPIViewMixin,
                            generics.RetrieveUpdateDestroyAPIView):
    def get_view_name(self) -> str:
        return "Project"


class ProjectContributorAPIViewMixin:
    queryset = Contributor.objects.prefetch_related('project', 'user')
    serializer_class = ContributorSerializer
    lookup_url_kwarg = "user_id"
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Self.kwargs.project_id
        queryset = queryset.filter(
            Q(user=self.request.user)
            | Q(project__author=self.request.user)
        )
        return queryset


class ProjectContributorsAPIView(ProjectContributorAPIViewMixin,
                                generics.ListCreateAPIView):

    def get_view_name(self) -> str:
        return "Contributors"

    def perform_create(self, serializer):
        project = get_object_or_404(Project.objects.filter(Q(author=self.request.user)), pk=self.kwargs['project_id'])
        serializer.save(project=project)


class ProjectContributorIndexedAPIView(views.APIView):

    def get_view_name(self) -> str:
        return "Contributor"

    def delete(self, request, *args, **kwargs):
        project = get_object_or_404(Project.objects.filter(author=self.request.user), pk=kwargs["project_id"])
        contributors = Contributor.objects.filter(project=project, user_id=kwargs['user_id']).all()
        for contributor in contributors:
            contributor.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class ProjectIssueAPIViewMixin:
    queryset = Issue.objects.prefetch_related('project')
    serializer_class = IssueSerializer
    lookup_url_kwarg = "issue_id"
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset().filter(
        )
        return queryset


class ProjectIssuesAPIView(ProjectIssueAPIViewMixin,
                          generics.ListCreateAPIView):
    def get_view_name(self) -> str:
        return "Issues"

    def perform_create(self, serializer):
        project = get_object_or_404(Project.objects, pk=self.kwargs['project_id'])
        serializer.save(project=project)


class ProjectIssueIndexedAPIView(ProjectIssueAPIViewMixin,
                                 generics.RetrieveUpdateDestroyAPIView):
    pass
