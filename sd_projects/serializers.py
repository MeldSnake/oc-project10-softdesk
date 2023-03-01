from collections import OrderedDict
from django.contrib.auth.models import User
from rest_framework import (serializers, validators as drf_validators)
from . import models
from django.shortcuts import get_object_or_404
from sd_projects import validators


class NoUpdateMixin(serializers.ModelSerializer):
    def get_extra_kwargs(self):
        kwargs = super().get_extra_kwargs()
        no_update_fields = getattr(self.Meta, "no_update_field", None)

        if self.instance and no_update_fields:
            for field in no_update_fields:
                kwargs.setdefault(field, {})
                kwargs[field]["read_only"] = True

        return kwargs


class FullPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    def __init__(self, /, *args, serializer: serializers.BaseSerializer, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer = serializer

    def get_choices(self, cutoff):
        qs = self.get_queryset()
        if qs is None:
            return {}
        if cutoff is not None:
            qs = qs[:cutoff]
        return OrderedDict([
            (
                item.pk,
                self.display_value(item)
            ) for item in qs
        ])

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return value

    def to_representation(self, value):
        data = super().to_representation(value)
        obj = get_object_or_404(self.get_queryset(), pk=data)
        return self.serializer().to_representation(obj)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name"]
        depth = 1


class ContributorSerializer(NoUpdateMixin, serializers.ModelSerializer):
    user = FullPrimaryKeyRelatedField(serializer=UserSerializer, queryset=User.objects.all(), required=True)

    class Meta:
        model = models.Contributor
        depth = 1
        exclude = ["project"]
        no_update_fields = ['user']

    def validate_user(self, value: models.User):
        project_id = self.context['view'].kwargs['project_id']
        if not self.instance and value:
            try:
                _ = value.contributing_to.get(project_id=project_id)
            except models.Contributor.DoesNotExist:
                return value
            message = 'The fields {field_names} must make a unique set.'.format(field_names=', '.join(('project', 'user')))
            raise serializers.ValidationError(message, code='unique')
        return value



class CommentSerializer(NoUpdateMixin, serializers.ModelSerializer):

    author = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = models.Comment
        exclude = ['issue']
        depth = 1
        no_update_fields = ['author']


class IssueSerializer(NoUpdateMixin, serializers.ModelSerializer):

    author = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    assigned = FullPrimaryKeyRelatedField(serializer=UserSerializer, queryset=User.objects.all())
    # assigned_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.all(), source='assigned', label='assigned')
    # assigned_value = UserSerializer(read_only=True, source='assigned', label='assigned')
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Issue
        exclude = ['project']
        depth = 1
        no_update_fields = ['author']
        validators = [
            validators.UserIsCollaborator(user_field='assigned', project_slug='project_id')
        ]


class ProjectSerializer(NoUpdateMixin, serializers.ModelSerializer):

    author = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    contributors = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    issues = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Project
        fields = "__all__"
        depth = 1
        no_update_fields = ['author']
