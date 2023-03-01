from django.urls import path

from .views import (
    ProjectsAPIView,
    ProjectIndexedAPIView,
    ProjectContributorAPIView,
    ProjectContributorIndexedAPIView,
    ProjectIssueAPIView,
    ProjectIssueIndexedAPIView,
    ProjectCommentsAPIView,
    ProjectCommentsIndexedAPIView,
)

urls = [
    path("projects/", ProjectsAPIView.as_view()),
    path("projects/<int:project_id>/", ProjectIndexedAPIView.as_view()),
    path("projects/<int:project_id>/users/", ProjectContributorAPIView.as_view()),
    path("projects/<int:project_id>/users/<int:user_id>/", ProjectContributorIndexedAPIView.as_view()),
    path("projects/<int:project_id>/issues/", ProjectIssueAPIView.as_view()),
    path("projects/<int:project_id>/issues/<int:issue_id>/", ProjectIssueIndexedAPIView.as_view()),
    path("projects/<int:project_id>/issues/<int:issue_id>/comments/", ProjectCommentsAPIView.as_view()),
    path("projects/<int:project_id>/issues/<int:issue_id>/comments/<int:comment_id>/", ProjectCommentsIndexedAPIView.as_view()),
]
