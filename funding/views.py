from rest_framework import viewsets
from .models import Post, PostImage , Comment
from .serializers import CommentSerializer, PostImageSerializer, PostSerializer
from rest_framework.permissions import IsAuthenticated


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostImageViewSet(viewsets.ModelViewSet):
    queryset = PostImage.objects.all()
    serializer_class = PostImageSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('created_at')
    serializer_class = CommentSerializer


    def get_queryset(self):
        post_id = self.request.query_params.get('post_id')
        if post_id:
            return Comment.objects.filter(post_id=post_id, parent__isnull=True)
        return Comment.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

