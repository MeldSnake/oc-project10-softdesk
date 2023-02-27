from django.urls import path

from .views import (
    ProjectContributorIndexedAPIView,
    ProjectContributorsAPIView,
    ProjectIndexedAPIView,
    ProjectIssueIndexedAPIView,
    ProjectIssuesAPIView,
    ProjectsAPIView,
)

# projects_issues_router = routers.NestedSimpleRouter(projects_router)

# projects_issues_comments_router = routers.NestedSimpleRouter(projects_issues_router)

urls = [
    path("projects/", ProjectsAPIView.as_view()),
    path("projects/<int:project_id>/", ProjectIndexedAPIView.as_view()),
    path("projects/<int:project_id>/users/", ProjectContributorsAPIView.as_view()),
    path("projects/<int:project_id>/users/<int:user_id>/", ProjectContributorIndexedAPIView.as_view()),
    path("projects/<int:project_id>/issues/", ProjectIssuesAPIView.as_view()),
    path("projects/<int:project_id>/issues/<int:issue_id>/", ProjectIssueIndexedAPIView.as_view()),
]
