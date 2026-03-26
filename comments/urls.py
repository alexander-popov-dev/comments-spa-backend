from django.urls import include, path
from rest_framework.routers import SimpleRouter

from comments.views import CommentViewSet

router = SimpleRouter()
router.register(prefix="comment", viewset=CommentViewSet, basename="comment")

urlpatterns = [
    path("v1/", include(router.urls)),
]
