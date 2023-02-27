from django.shortcuts import get_object_or_404
from rest_framework import validators, fields, serializers
from sd_projects.models import User, Project
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


class UserIsCollaborator:
    requires_context = True

    def __init__(self, project_field: str | None = None, project_slug: str | None = None,
                 user_field: str | None = None, user_slug: str | None = None) -> None:
        super().__init__()
        # TODO Assert here
        self.project_field = project_field
        self.project_slug = project_slug
        # TODO Assert here
        self.user_field = user_field
        self.user_slug = user_slug

    def __call__(self, value, field: fields.Field) -> None:
        if self.user_field is not None:
            user = value[self.user_field]
        else:
            user = get_object_or_404(User.objects.all(), field.context['view'].kwargs[self.user_slug])
        if self.project_field is not None:
            project = value[self.project_field].pk
        else:
            project_id = field.context['view'].kwargs[self.project_slug]
        try:
            project = Project.objects.filter(
                Q(author=user)
                | Q(contributors__user=user)
            ).get(pk=project_id)
        except ObjectDoesNotExist as _:
            raise serializers.ValidationError(f"User {user.get_full_name()} is not a contributor of the project {project_id}")