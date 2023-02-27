from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Project(models.Model):

    class ProjectType(models.IntegerChoices):
        BACKEND = 0, _('back-end')
        FRONTEND = 1, _('front-end')
        IOS = 2, _('iOS')
        ANDROID = 3, _('android')

    title = models.CharField(max_length=150, unique=True)
    description = models.CharField(max_length=255, blank=True)

    ptype = models.PositiveSmallIntegerField(_("type"), name="type", choices=ProjectType.choices)

    author = models.ForeignKey(User, related_name='projects', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")

    def __str__(self):
        return self.name


class Contributor(models.Model):

    class ContributorPermission(models.IntegerChoices):
        READ = 1, _('read')
        WRITE = 2, _('write')
        DELETE = 3, _('delete')

    class ContributorRole(models.IntegerChoices):
        OWNER = 1, _('owner')
        CONTRIBUTOR = 2, _('contributor')

    permission = models.PositiveSmallIntegerField(choices=ContributorPermission.choices)
    role = models.PositiveSmallIntegerField(choices=ContributorRole.choices)

    user = models.ForeignKey(User, related_name='contributing_to', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='contributors', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("contributor")
        verbose_name_plural = _("contributors")
        constraints = [models.constraints.UniqueConstraint('user', 'project', name='unique_user_project')]

    def __str__(self):
        return self.user.first_name + self.user.last_name + self.role


class Issue(models.Model):
    class IssuePriority(models.IntegerChoices):
        LOW = 0, _('low')
        AVERAGE = 1, _('average')
        HIGH = 2, _('high')

    class IssueTag(models.IntegerChoices):
        BUG = 0, _('bug')
        IMPROVEMENT = 1, _('improvement')
        TASK = 2, _('task')

    class IssueStatus(models.IntegerChoices):
        TODO = 0, _('todo')
        PENDING = 1, _('pending')
        FINISHED = 2, _('finished')

    title = models.CharField(max_length=50)
    description = models.CharField(max_length=320)
    created_time = models.DateTimeField(auto_now_add=True)

    status = models.PositiveSmallIntegerField(choices=IssueStatus.choices)
    tag = models.PositiveSmallIntegerField(choices=IssueTag.choices)
    priority = models.PositiveSmallIntegerField(choices=IssuePriority.choices)

    project = models.ForeignKey(Project, related_name='issues', on_delete=models.CASCADE)
    assigned = models.ForeignKey(User, related_name='assigned_issues', on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(User, related_name='created_issues', on_delete=models.SET_NULL, null=True)

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
