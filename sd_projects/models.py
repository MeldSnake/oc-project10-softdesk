from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from . import enums


class Project(models.Model):

    title = models.CharField(max_length=150, unique=True)
    description = models.CharField(max_length=255, blank=True)

    ptype = models.PositiveSmallIntegerField(_("type"), name="type", choices=enums.PROJECT_TYPE)

    author = models.ForeignKey(User, related_name='projects', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")

    def __str__(self):
        return self.name


class Contributor(models.Model):

    permission = models.PositiveSmallIntegerField(choices=enums.CONTRIBUTOR_PERMISSION)
    role = models.PositiveSmallIntegerField(choices=enums.CONTRIBUTOR_ROLE)

    user = models.ForeignKey(User, related_name='contributing_to', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='contributors', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("contributor")
        verbose_name_plural = _("contributors")

    def __str__(self):
        return self.user.first_name + self.user.last_name + self.role


class Issue(models.Model):

    title = models.CharField(max_length=50)
    description = models.CharField(max_length=320)
    created_time = models.DateTimeField(auto_now_add=True)

    status = models.PositiveSmallIntegerField(choices=enums.ISSUE_STATUS)
    tag = models.PositiveSmallIntegerField(choices=enums.ISSUE_TAG)
    priority = models.PositiveSmallIntegerField(choices=enums.PROJECT_TYPE)

    project = models.ForeignKey(Project, related_name='issues', on_delete=models.CASCADE)
    assigned = models.ForeignKey(User, related_name='assigned_issues', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _("issue")
        verbose_name_plural = _("issues")

    def __str__(self):
        return self.name


class Comment(models.Model):

    description = models.CharField(max_length=320)
    created_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, related_name='comments', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    def __str__(self):
        return self.name
