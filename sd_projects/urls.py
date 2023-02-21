from rest_framework import routers
from .views import ProjectViewSet

projects_router = routers.SimpleRouter()
projects_router.register('projects', ProjectViewSet, basename='projects')
