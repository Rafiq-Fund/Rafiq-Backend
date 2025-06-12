from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, CommentViewSet, PostImageViewSet,
    PostViewSet, DonationViewSet, TagViewSet, RatingViewSet
)

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'post-images', PostImageViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'donations', DonationViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ratings', RatingViewSet, basename='rating')

urlpatterns = router.urls
