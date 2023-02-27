from django.db import models
from typing import Any, Type, TypeVar
from .models import (Contributor, Project, Issue, Comment)
from rest_framework import (views, permissions, request)

MT = TypeVar('MT', bound=models.base.Model)


class IsValidIssuePermission(permissions.BasePermission):
    def has_permission(self, request: request.Request, view: views.APIView) -> bool:
        try:
            _ = Issue.objects.get(
                pk=view.kwargs["issue_id"],
                project_id=view.kwargs["project_id"],
            )
            return True
        except models.Model.DoesNotExist:
            return False


class IsValidCommentPermission(permissions.BasePermission):
    def has_permission(self, request: request.Request, view: views.APIView) -> bool:
        try:
            _ = Comment.objects.get(
                pk=view.kwargs["comment_id"],
                issue_id=view.kwargs["issue_id"],
            )
            return True
        except models.Model.DoesNotExist:
            return False


class CheckProjectAccessPermission(permissions.BasePermission):
    """
    Check if the current user is a contributor of the current project.
    It will also check wether the user can write on a project object.
    """
    def has_permission(self, request: request.Request, view: views.APIView) -> bool:
        if (request.method or "").upper() == "POST":
            return True
        try:
            _ = Contributor.objects.get(project_id=view.kwargs["project_id"], user=request.user)  # type: ignore
        except models.Model.DoesNotExist:
            return False
        return True

    def has_object_permission(self, request: request.Request, view: views.APIView, obj: Any) -> bool:
        if (request.method or "").upper() == "POST":
            return True
        if isinstance(obj, Project):
            try:
                contributor = Contributor.objects.get(project=obj, user=request.user)  # type: ignore
            except models.Model.DoesNotExist:
                return False
            if (request.method or "").upper() not in permissions.SAFE_METHODS:
                return contributor.role == Contributor.ContributorRole.OWNER
        return True


class CheckContributorEditionPermission(permissions.BasePermission):
    """
    Check if the current user is the owner of the project and thus can modify/delete a contributor.
    On create check if the current user is the owner of the project.
    """
    def has_object_permission(self, request: request.Request, view: views.APIView, obj: Any) -> bool:
        if isinstance(obj, Contributor):
            if (request.method or "").upper() == "POST":
                try:
                    contributor = Contributor.objects.get(user=request.user, project_id=view.kwargs["project_id"])  # type: ignore
                    return contributor.role == Contributor.ContributorRole.OWNER
                except models.Model.DoesNotExist:
                    return False
            if (request.method or "").upper() == "DELETE":
                if obj.user == request.user and obj.role == Contributor.ContributorRole.OWNER:
                    return False
                return obj.user == request.user or obj.role == Contributor.ContributorRole.OWNER
            elif (request.method or "").upper() not in permissions.SAFE_METHODS:
                return obj.user == request.user or obj.role == Contributor.ContributorRole.OWNER
        return True


def CheckModelAuthorAccessPermission(MTType: Type[MT]):
    """
    Create a permission validator that check if the current user is the author of the object on write.
    On create the validator return True
    """

    class CheckModelAuthorAccessPermission(permissions.BasePermission):
        """
        Check if the current user is the author of the current issue when modifying/deleting.
        On create return True
        """

        def has_object_permission(self, request: request.Request, view: views.APIView, obj: MT) -> bool:
            if isinstance(obj, MTType):
                if (request.method or "").upper() == "POST":
                    return True
                if (request.method or "").upper() not in permissions.SAFE_METHODS:
                    return obj.author == request.user  # type: ignore
                return True
            return super().has_object_permission(request, view, obj)

    return CheckModelAuthorAccessPermission
