from django.db import models
from typing import Generic, TypeVar
from rest_framework import mixins, generics
from .serializers import (ProjectSerializer,
                          ContributorSerializer,
                          IssueSerializer)
from .models import (Contributor, Project, Issue, Comment)
from django.shortcuts import get_object_or_404
from rest_framework import (response, status, authentication, permissions)
from .permissions import (
    IsValidCommentPermission,
    IsValidIssuePermission,
    CheckProjectAccessPermission,
    CheckContributorEditionPermission,
    CheckModelAuthorAccessPermission
)

MT = TypeVar('MT', bound=models.base.Model)


class FullModelAPIView(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       generics.GenericAPIView[MT],
                       Generic[MT]):

    def get(self, request, *args, **kwargs):
        lookup_arg = self.lookup_url_kwarg or self.lookup_field
        if lookup_arg in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ProjectAPIView(FullModelAPIView[Project]):
    queryset = Project.objects.prefetch_related('contributors', 'author')
    serializer_class = ProjectSerializer
    lookup_url_kwarg = "project_id"
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        CheckProjectAccessPermission
    ]

    def get_view_name(self) -> str:
        return "Projects"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset.filter(
            models.Q(author=self.request.user)
            | models.Q(contributors__user=self.request.user)
        )
        return queryset


class ProjectContributorAPIView(FullModelAPIView[Contributor]):
    queryset = Contributor.objects.prefetch_related('project', 'user')
    serializer_class = ContributorSerializer
    lookup_url_kwarg = "user_id"
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        CheckProjectAccessPermission,
        CheckContributorEditionPermission,
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            project_id=self.kwargs["project_id"]
        )
        return queryset

    def perform_create(self, serializer):
        project = get_object_or_404(Project.objects, self.kwargs["project_id"])
        serializer.save(project=project)

    def delete(self, request, *args, **kwargs):
        # TODO Permission OWNER is not deletable, only when project is deleted
        # TODO Permission on objects, owner can delete/change all contributors of project, contributors can remove themselves only
        contributors = self.get_queryset().filter(
            role__ne=Contributor.ContributorRole.OWNER
        ).all()
        for contributor in contributors:
            contributor.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class ProjectIssueAPIView(FullModelAPIView[Issue]):
    queryset = Issue.objects.prefetch_related('project')
    serializer_class = IssueSerializer
    lookup_url_kwarg = "issue_id"
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        IsValidIssuePermission,
        CheckProjectAccessPermission,
        CheckModelAuthorAccessPermission(Issue),
    ]

    def get_queryset(self):
        return super().get_queryset().filter(
            project_id=self.kwargs["project_id"]
        )

    def perform_create(self, serializer):
        # TODO Permission only creator can delete the issue
        project = get_object_or_404(Project.objects, self.kwargs["project_id"])
        serializer.save(project=project)


class ProjectCommentsAPIView(FullModelAPIView[Comment]):
    queryset = Comment.objects.prefetch_related('project')
    serializer_class = IssueSerializer
    lookup_url_kwarg = "issue_id"
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        IsValidCommentPermission,
        CheckProjectAccessPermission,
        CheckModelAuthorAccessPermission(Comment),
    ]

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            issue_id=self.kwargs["issue_id"],
            issue_project_id=self.kwargs["project_id"],
        )
        return queryset
