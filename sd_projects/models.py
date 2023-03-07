from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Project(models.Model):

    class ProjectType(models.IntegerChoices):
        BACKEND = 0, _('back-end')
        FRONTEND = 1, _('front-end')
        IOS = 2, _('iOS')
        ANDROID = 3, _('android')

    title = models.CharField(max_length=150, unique=True, help_text="Title of the project")
    description = models.CharField(max_length=255, blank=True, help_text="Short description of the project")

    ptype = models.PositiveSmallIntegerField(_("type"), name="type", choices=ProjectType.choices, help_text="""
Type of the project
- 0: Back-end
- 1: Front-end
- 2: iOS
- 3: Android
""")

    author = models.ForeignKey(User, related_name='projects', on_delete=models.CASCADE, help_text="Author of the project")

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")


class Contributor(models.Model):

    class ContributorPermission(models.IntegerChoices):
        READ = 1, _('read')
        WRITE = 2, _('write')
        DELETE = 3, _('delete')

    class ContributorRole(models.IntegerChoices):
        OWNER = 1, _('owner')
        CONTRIBUTOR = 2, _('contributor')

    permission = models.PositiveSmallIntegerField(choices=ContributorPermission.choices, help_text="""
Permission of the contributor for the project
- 1: Read only
- 2: Read, Write
- 3: Read, Write and Delete
""")
    role = models.PositiveSmallIntegerField(choices=ContributorRole.choices, help_text="""
Role of the contributor for the project
- 1: Owner
- 2: Contributor
""")

    user = models.ForeignKey(User, related_name='contributing_to', on_delete=models.CASCADE, help_text="User being the actual contributor")
    project = models.ForeignKey(Project, related_name='contributors', on_delete=models.CASCADE, help_text="Project of which this contributor is contributing to")

    class Meta:
        verbose_name = _("contributor")
        verbose_name_plural = _("contributors")
        constraints = [models.constraints.UniqueConstraint('user', 'project', name='unique_user_project')]


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

    title = models.CharField(max_length=50, help_text="Title of the issue")
    description = models.CharField(max_length=320, help_text="Short description of the issue")
    created_time = models.DateTimeField(auto_now_add=True, help_text="Date and time of creation of the issue")

    status = models.PositiveSmallIntegerField(choices=IssueStatus.choices, help_text="""
Status of the issue
- 0: Todo
- 1: Pending
- 2: Finished
""")
    tag = models.PositiveSmallIntegerField(choices=IssueTag.choices, help_text="""
Tag attributed to the issue
- 0: Bug
- 1: Improvement
- 2: Task
""")
    priority = models.PositiveSmallIntegerField(choices=IssuePriority.choices, help_text="""
Priority of the issue
- 0: Low
- 1: Average
- 2: High
""")

    project = models.ForeignKey(Project, related_name='issues', on_delete=models.CASCADE, help_text="Project to which this issue is mapped")
    assigned = models.ForeignKey(User, related_name='assigned_issues', on_delete=models.SET_NULL, null=True, help_text="Contributor assigned to solving the issue", default=None)
    author = models.ForeignKey(User, related_name='created_issues', on_delete=models.CASCADE, help_text="Author of the issue")

    class Meta:
        verbose_name = _("issue")
        verbose_name_plural = _("issues")


class Comment(models.Model):

    description = models.CharField(max_length=320, help_text="Short commentary content")
    created_time = models.DateTimeField(auto_now_add=True, help_text="Date and time of creation of the commentary")
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE, help_text="Author of the commentary")
    issue = models.ForeignKey(Issue, related_name='comments', on_delete=models.CASCADE, help_text="Issue to which this commentary is mapped")

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")
