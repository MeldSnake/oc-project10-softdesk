from django.contrib.auth.models import User
from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name"]
        depth = 1


class Contributor(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = models.Contributor
        exclude = ['project']
        depth = 1


class CommentSerializer(serializers.ModelSerializer):

    author = UserSerializer()

    class Meta:
        model = models.Comment
        exclude = ['issue']
        depth = 1


class IssueSerializer(serializers.ModelSerializer):

    assigned = UserSerializer()
    comments = CommentSerializer(many=True)

    class Meta:
        model = models.Issue
        fields = "__all__"
        depth = 1


class ProjectSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    contributors = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    issues = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Project
        fields = "__all__"
        depth = 1


class ProjectCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        exclude = ['author']
