from django.utils import timezone
from rest_framework import serializers
from .models import Post, PostImage, Donation, Comment

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'replies']
        read_only_fields = ['created_at']

    def get_replies(self, obj):
        """Recursive serialization for comment replies with depth limit"""
        max_depth = 3  # Prevent infinite recursion
        return self.get_nested_replies(obj, max_depth)
    
    def get_nested_replies(self, obj, depth):
        if depth <= 0:
            return []
        queryset = obj.replies.all()
        serializer = CommentSerializer(queryset, many=True, context={
            'depth': depth - 1
        })
        return serializer.data

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image']
        read_only_fields = ['id']

class DonationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Donation
        fields = ['id', 'user', 'amount', 'created_at', 'is_anonymous', 'message']
        read_only_fields = ['id', 'created_at']
    
    def to_representation(self, instance):
        """Hide user info for anonymous donations"""
        data = super().to_representation(instance)
        if instance.is_anonymous:
            data['user'] = 'Anonymous'
        return data

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    donations = DonationSerializer(many=True, read_only=True)
    current_amount = serializers.SerializerMethodField(read_only=True)
    funding_percentage = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'created_at', 
            'target_amount', 'deadline', 'comments', 'images',
            'donations', 'current_amount', 'funding_percentage'
        ]
        read_only_fields = [
            'id', 'created_at', 'current_amount', 
            'funding_percentage', 'comments', 'images', 'donations'
        ]

    def get_current_amount(self, obj):
        return obj.current_amount

    def get_funding_percentage(self, obj):
        return obj.funding_percentage

    def validate(self, attrs):
        """
        Custom validation for deadline and target amount
        Note: Using 'attrs' as parameter name to match base class signature
        """
        # Validate deadline if provided
        if 'deadline' in attrs:
            if attrs['deadline'] < timezone.now():
                raise serializers.ValidationError({
                    'deadline': 'Deadline must be in the future'
                })
        
        # Validate target amount if provided
        if 'target_amount' in attrs:
            if attrs['target_amount'] < 1:
                raise serializers.ValidationError({
                    'target_amount': 'Target amount must be at least 1.00'
                })
        
        return attrs

    def create(self, validated_data):
        """Automatically set author to current user"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)