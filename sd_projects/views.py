from django.db import models
from typing import Generic, TypeVar
from rest_framework import mixins, generics
from .serializers import (
    ProjectSerializer,
    ContributorSerializer,
    IssueSerializer,
    CommentSerializer,
)
from .models import Contributor, Project, Issue, Comment
from django.shortcuts import get_object_or_404
from rest_framework import (
    response,
    status,
    authentication,
    permissions,
    serializers,
)
from .permissions import (
    IsContributor,
    IsProjectOwnerCreate,
    IsProjectOwnerEdit,
    IsProjectOwnerOrSelf,
    IsProjectOwnerOrAuthor,
)

MT = TypeVar("MT", bound=models.base.Model)


class FullModelAPIView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
    Generic[MT],
):
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


class ProjectsAPIMixin:
    queryset = Project.objects.prefetch_related("contributors", "author")
    serializer_class = ProjectSerializer
    lookup_url_kwarg = "project_id"
    authentication_classes = [
        authentication.SessionAuthentication,
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset.filter(models.Q(contributors__user=self.request.user))
        return queryset


class ProjectsAPIView(  # type: ignore
    ProjectsAPIMixin,
    generics.ListCreateAPIView,
):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_view_name(self) -> str:
        return "Projects"

    def perform_create(self, serializer: serializers.BaseSerializer[Project]) -> None:
        project = serializer.save(
            author=self.request.user,
        )
        contributor = Contributor(
            permission=Contributor.ContributorPermission.DELETE,
            role=Contributor.ContributorRole.OWNER,
            user=project.author,
            project=project,
        )
        contributor.save()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset.filter(models.Q(contributors__user=self.request.user))
        return queryset


class ProjectIndexedAPIView(  # type: ignore
    ProjectsAPIMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    permission_classes = [
        permissions.IsAuthenticated,
        IsContributor,
        IsProjectOwnerEdit,
    ]

    def get_view_name(self) -> str:
        return "Project"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset.filter(models.Q(contributors__user=self.request.user))
        return queryset


class ProjectContributorAPIMixin:
    queryset = Contributor.objects.prefetch_related("project", "user")
    serializer_class = ContributorSerializer
    lookup_url_kwarg = "user_id"
    authentication_classes = [
        authentication.SessionAuthentication,
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(project_id=self.kwargs["project_id"])
        return queryset


class ProjectContributorAPIView(  # type: ignore
    ProjectContributorAPIMixin,
    generics.ListCreateAPIView,
):
    permission_classes = [
        permissions.IsAuthenticated,
        IsContributor,
        IsProjectOwnerCreate,
    ]

    def get_view_name(self):
        return "Contributors"

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        serializer.save(project=project)


class ProjectContributorIndexedAPIView(  # type: ignore
    ProjectContributorAPIMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    permission_classes = [
        permissions.IsAuthenticated,
        IsContributor,
        IsProjectOwnerOrSelf,
    ]

    def get_view_name(self):
        return "Contributor"

    def delete(self, request, *args, **kwargs):
        # TODO Permission OWNER is not deletable, only when project is deleted
        # TODO Permission on objects, owner can delete/change all contributors of project, contributors can remove themselves only
        contributors = (
            self.get_queryset().filter(role__ne=Contributor.ContributorRole.OWNER).all()
        )
        for contributor in contributors:
            contributor.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class ProjectIssueAPIMixin:
    queryset = Issue.objects.prefetch_related("project")
    serializer_class = IssueSerializer
    lookup_url_kwarg = "issue_id"
    authentication_classes = [
        authentication.SessionAuthentication,
        IsContributor,
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(project_id=self.kwargs["project_id"])
        return queryset


class ProjectIssueAPIView(  # type: ignore
    ProjectIssueAPIMixin,
    generics.ListCreateAPIView,
):
    permission_classes = [
        permissions.IsAuthenticated,
        IsContributor,
    ]

    def get_view_name(self):
        return "Issues"

    def perform_create(self, serializer):
        project = get_object_or_404(Project.objects, pk=self.kwargs["project_id"])
        serializer.save(project=project, author=self.request.user)


class ProjectIssueIndexedAPIView(  # type: ignore
    ProjectIssueAPIMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    permission_classes = [
        permissions.IsAuthenticated,
        IsContributor,
        IsProjectOwnerOrAuthor,
    ]

    def get_view_name(self):
        return "Issue"


class ProjectCommentsAPIMixin:
    queryset = Comment.objects.prefetch_related("issue")
    serializer_class = CommentSerializer
    lookup_url_kwarg = "comment_id"
    authentication_classes = [
        authentication.SessionAuthentication,
    ]

    def get_view_name(self) -> str:
        return "Comment"

    def get_queryset(self):
        queryset = super().get_queryset() \
            .filter(
                issue_id=self.kwargs["issue_id"],
                issue__project_id=self.kwargs["project_id"],
            )
        return queryset


class ProjectCommentsAPIView(  # type: ignore
    ProjectCommentsAPIMixin,
    generics.ListCreateAPIView,
):
    permission_classes = [
        permissions.IsAuthenticated,
        IsContributor,
    ]

    def get_view_name(self) -> str:
        return "Comments"

    def perform_create(self, serializer):
        issue = get_object_or_404(Issue.objects, pk=self.kwargs["issue_id"])
        serializer.save(issue=issue, author=self.request.user)


class ProjectCommentsIndexedAPIView(  # type: ignore
    ProjectCommentsAPIMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    permission_classes = [
        permissions.IsAuthenticated,
        IsContributor,
        IsProjectOwnerOrAuthor,
    ]

    def get_view_name(self) -> str:
        return "Comment"
