from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers
from .models import Post, PostImage, Donation, Comment, Category, Tag, Rating

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'parent', 'content', 'created_at', 'replies']
        read_only_fields = ['id', 'user', 'created_at', 'replies']

    def get_replies(self, obj):
        depth = self.context.get('depth', 3)
        if depth <= 0:
            return []
        children = obj.replies.all().order_by('created_at')
        serializer = CommentSerializer(children, many=True, context={'depth': depth - 1})
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
        fields = ['id', 'user', 'amount', 'created_at', 'message']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'user', 'post', 'value', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_value(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        post = validated_data.get('post')

        if Rating.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError("You have already rated this post.")

        validated_data['user'] = user
        return super().create(validated_data)

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    donations = DonationSerializer(many=True, read_only=True)
    current_amount = serializers.SerializerMethodField(read_only=True)
    funding_percentage = serializers.SerializerMethodField(read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)

    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, source='category'
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, source='tags'
    )

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'category', 'category_id',
            'tags', 'tag_ids', 'created_at', 'target_amount',
            'start_time', 'end_time', 'is_canceled',
            'comments', 'images', 'donations',
            'current_amount', 'funding_percentage', 'average_rating'
        ]
        read_only_fields = [
            'id', 'created_at', 'current_amount', 'funding_percentage',
            'comments', 'images', 'donations', 'average_rating', 'author', 'category', 'tags'
        ]

    def get_comments(self, obj):
        top_level_comments = obj.comments.filter(parent__isnull=True).order_by('created_at')
        return CommentSerializer(top_level_comments, many=True).data

    def get_current_amount(self, obj):
        return obj.current_amount

    def get_average_rating(self, obj):
        return obj.average_rating

    def get_funding_percentage(self, obj):
        if obj.target_amount:
            return round((Decimal(obj.current_amount) / obj.target_amount) * 100, 2)
        return 0

    def validate(self, attrs):
        now = timezone.now()
        end_time = attrs.get('end_time')
        start_time = attrs.get('start_time')

        if end_time and end_time < now:
            raise serializers.ValidationError({'end_time': 'End time must be in the future'})

        if start_time and end_time and start_time > end_time:
            raise serializers.ValidationError({'start_time': 'Start time must be before end time'})

        return attrs

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        validated_data['author'] = self.context['request'].user
        post = Post.objects.create(**validated_data)
        post.tags.set(tags_data)
        return post

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags_data is not None:
            instance.tags.set(tags_data)
        return instance
