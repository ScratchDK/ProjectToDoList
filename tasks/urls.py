from rest_framework.routers import DefaultRouter

import tasks.views as views

app_name = "tasks"

router = DefaultRouter()

router.register("tasks", views.TaskViewSet, basename="tasks")
router.register("categories", views.CategoryViewSet, basename="categories")

urlpatterns = [] + router.urls
