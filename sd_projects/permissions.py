from typing import Any
from .models import (Contributor, Issue, Comment, User)
from rest_framework import (views, permissions, request)


class IsContributor(permissions.BasePermission):
    """
    This allow a user access to a resource only if it is a contributor to the current project.
    """

    def has_permission(self, request: request.Request, view: views.APIView) -> bool:
        if "project_id" in view.kwargs:
            try:
                _ = Contributor.objects.get(
                    project_id=view.kwargs["project_id"],
                    user=request.user  # type: ignore
                )
            except Contributor.DoesNotExist:
                return False
        return True


class IsProjectOwnerEdit(permissions.BasePermission):
    """
    This permit the currenty user to edit/delete a resource only if it is the owner of the current project.
    """

    def has_object_permission(self, request: request.Request, view: views.APIView, _: Any) -> bool:
        if "project_id" in view.kwargs:
            if (request.method or "").upper() in ["PATCH", "PUT", "DELETE"]:
                try:
                    contributor = Contributor.objects.get(
                        project_id=view.kwargs["project_id"],
                        user=request.user  # type: ignore
                    )
                except Contributor.DoesNotExist:
                    return False
                return contributor.role == Contributor.ContributorRole.OWNER
            return True
        return False


class IsProjectOwnerCreate(permissions.BasePermission):
    """
    This permit the creation only if the current user is the current project owner.
    Used by POST /project/<project_id:int>/users/ exclusively.
    """

    def has_permission(self, request: request.Request, view: views.APIView) -> bool:
        if "project_id" in view.kwargs:
            if (request.method or "").upper() == "POST":
                try:
                    contributor = Contributor.objects.get(
                        project_id=view.kwargs["project_id"],
                        user=request.user  # type: ignore
                    )
                except Contributor.DoesNotExist:
                    return False
                return contributor.role == Contributor.ContributorRole.OWNER
            return True
        return False


class IsProjectOwnerOrSelf(permissions.BasePermission):
    """
    This permit the current user to edit/delete a resource only if it is the owner of the current project.
    But also permit the deletion of the resource if the user bound to the resource is the current user.
    """

    def has_object_permission(self, request: request.Request, view: views.APIView, obj: User) -> bool:
        if request.method in ["PUT", "PATCH", "DELETE"]:
            if "project_id" in view.kwargs:
                if obj == request.user and request.method == "DELETE":
                    return True
                try:
                    contributor = Contributor.objects.get(
                        project_id=view.kwargs["project_id"],
                        user=obj.user  # type: ignore
                    )
                except Contributor.DoesNotExist:
                    return False
                return contributor.role == Contributor.ContributorRole.OWNER
        return True


class IsProjectOwnerOrAuthor(permissions.BasePermission):
    """
    This permit the current user to edit/delete a resource only if it is the owner of the current project or the author of the resource.
    """

    def has_object_permission(self, request: request.Request, view: views.APIView, obj: Issue | Comment) -> bool:
        if request.method in ["PUT", "PATCH", "DELETE"]:
            if obj.author == request.user:
                return True
            try:
                contributor = Contributor.objects.get(
                    project_id=view.kwargs["project_id"],
                    user=obj  # type: ignore
                )
            except Contributor.DoesNotExist:
                return False
            return contributor.role == Contributor.ContributorRole.OWNER
        return True
