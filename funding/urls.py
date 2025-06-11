from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, PostImageViewSet, PostViewSet, DonationViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'post-images', PostImageViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'donations', DonationViewSet)

urlpatterns = router.urls
