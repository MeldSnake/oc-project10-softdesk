from collections import OrderedDict
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from rest_framework import (serializers, validators as drf_validators)
from . import models
from rest_framework.generics import get_object_or_404
from sd_projects import validators


class NoUpdateMixin(serializers.ModelSerializer):
    
    def get_extra_kwargs(self):
        kwargs = super().get_extra_kwargs()
        create_only_fields = getattr(self.Meta, "create_only_fields", None)

        if self.instance and create_only_fields:
            for field in create_only_fields:
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
    user = FullPrimaryKeyRelatedField(serializer=UserSerializer, queryset=User.objects.all())

    class Meta:
        model = models.Contributor
        depth = 1
        exclude = ["project"]
        create_only_fields = ['user']
        extra_kwargs = {
            'role': {'read_only': True}
        }

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
        create_only_fields = ['author']


class IssueSerializer(NoUpdateMixin, serializers.ModelSerializer):

    author = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    assigned = FullPrimaryKeyRelatedField(required=False, serializer=UserSerializer, queryset=User.objects.all())
    # assigned_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.all(), source='assigned', label='assigned')
    # assigned_value = UserSerializer(read_only=True, source='assigned', label='assigned')
    # comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Issue
        exclude = ['project']
        depth = 1
        create_only_fields = ['author']
        validators = [
            validators.UserIsCollaborator(user_field='assigned', project_slug='project_id', nullable_user=True)
        ]


class ProjectSerializer(NoUpdateMixin, serializers.ModelSerializer):

    author = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    # contributors = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # issues = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Project
        fields = "__all__"
        depth = 1
        create_only_fields = ['author']


class UserCreationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'password2',
            'email',
            'first_name',
            'last_name',
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            # 'email': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Invalid confirmation password", "password_confirm")
        return attrs

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
