from django.urls import include, path
from rest_framework.routers import SimpleRouter

from comments.views import CommentViewSet

router = SimpleRouter()
router.register("comment", CommentViewSet)

urlpatterns = [
    path("v1/", include(router.urls)),
]
