from tokenize import Comment
from rest_framework import serializers
from .models import Post, PostImage

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'parent', 'content', 'created_at', 'replies']

    def get_replies(self, obj):
        queryset = obj.replies.all()
        return CommentSerializer(queryset, many=True).data

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image']

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)  
    images = PostImageSerializer(many=True, read_only=True)  

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'comments','created_at', 'images']


