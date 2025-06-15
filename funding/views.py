from django.forms import ValidationError
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Post, PostImage, Comment, Donation, Tag, Rating
from .serializers import (
    CategorySerializer, CommentSerializer, PostImageSerializer,
    PostSerializer, DonationSerializer, TagSerializer, RatingSerializer
)



class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'tags']


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostImageViewSet(viewsets.ModelViewSet):
    queryset = PostImage.objects.all()
    serializer_class = PostImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()  
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.request.query_params.get('post_id')
        if post_id:
            return Comment.objects.filter(post_id=post_id, parent__isnull=True).order_by('created_at')
        return Comment.objects.all().order_by('created_at')  

    def perform_create(self, serializer):
        post_id = self.request.data.get('post')
        if not post_id:
            raise ValidationError({"post": "This field is required."})

        parent_id = self.request.data.get('parent')
        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id)
            except Comment.DoesNotExist:
                raise ValidationError({"parent": "Invalid parent comment ID."})

        serializer.save(user=self.request.user, post_id=post_id, parent=parent)

class DonationViewSet(viewsets.ModelViewSet):
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Donation.objects.all()

    def get_queryset(self):
        post_id = self.request.query_params.get('post_id')
        if post_id:
            return Donation.objects.filter(post_id=post_id)
        return Donation.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.request.query_params.get('post_id')
        if post_id:
            return Rating.objects.filter(post_id=post_id)
        return Rating.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
