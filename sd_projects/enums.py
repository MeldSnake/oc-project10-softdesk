from django.utils.translation import gettext_lazy as _

CONTRIBUTOR_PERMISSION = (
    (0, _("unauthorized")),
    (1, _("readonly")),
    (2, _("write")),
)

CONTRIBUTOR_ROLE = (
    (0, _("no role")),
    (1, _("owner")),
    (2, _("contributor")),
)

PROJECT_TYPE = (
    (0, _("back-end")),
    (1, _("front-end")),
    (2, _("iOS")),
    (3, _("android")),
)

ISSUE_PRIORITY = (
    (0, _("low")),
    (1, _("average")),
    (2, _("high")),
)

ISSUE_TAG = (
    (0, _("bug")),
    (1, _("improvement")),
    (2, _("task")),
)

ISSUE_STATUS = (
    (0, _("todo")),
    (1, _("pending")),
    (2, _("finished")),
)
