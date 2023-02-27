from django.urls import include, path
from rest_framework import routers
from .views import (ProjectAPIView, ProjectIndexedAPIView,
                    ProjectContributorAPIView, ProjectContributorIndexedAPIView,
                    ProjectIssueAPIView, ProjectIssueIndexedAPIView)

# projects_issues_router = routers.NestedSimpleRouter(projects_router)

# projects_issues_comments_router = routers.NestedSimpleRouter(projects_issues_router)

urls = [
    path('projects/', ProjectAPIView.as_view()),
    path('projects/<int:project_id>/', ProjectIndexedAPIView.as_view()),
    path('projects/<int:project_id>/users/', ProjectContributorAPIView.as_view()),
    path('projects/<int:project_id>/users/<int:user_id>/', ProjectContributorIndexedAPIView.as_view()),
    path('projects/<int:project_id>/issues/', ProjectIssueAPIView.as_view()),
    path('projects/<int:project_id>/issues/<int:issue_id>/', ProjectIssueIndexedAPIView.as_view()),
]
