from collections import OrderedDict
from django.contrib.auth.models import User
from rest_framework import serializers, validators as rvalidators
from . import models
from django.shortcuts import get_object_or_404
from sd_projects import validators


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


class ContributorSerializer(serializers.ModelSerializer):

    user = FullPrimaryKeyRelatedField(serializer=UserSerializer, queryset=User.objects.all())

    class Meta:
        model = models.Contributor
        exclude = ['project']
        depth = 1
        validators = [
            # TODO Deduplication avoid for same user multiple times on same project.
        ]


class CommentSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = models.Comment
        exclude = ['issue']
        depth = 1


class IssueSerializer(serializers.ModelSerializer):

    assigned = FullPrimaryKeyRelatedField(serializer=UserSerializer, queryset=User.objects.all())
    # assigned_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.all(), source='assigned', label='assigned')
    # assigned_value = UserSerializer(read_only=True, source='assigned', label='assigned')
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Issue
        exclude = ['project']
        depth = 1
        validators = [
            validators.UserIsCollaborator(user_field='assigned', project_slug='project_id')
        ]


class ProjectSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    contributors = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    issues = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Project
        fields = "__all__"
        depth = 1
