from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1000.00,  # Default for existing and new rows
        validators=[MinValueValidator(1000.00)],  # Ensure value >= 1000
        help_text="Funding goal amount (minimum 1000)"
    )
    deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional funding deadline"
    )

    def __str__(self):
        return self.title

    @property
    def current_amount(self):
        return self.donations.aggregate(
            total=models.Sum('amount')
        )['total'] or 0.00


class PostImage(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='post_images/')

    def __str__(self):
        return f"Image for {self.post.title}"


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"


class Donation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donations'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='donations'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.amount} to {self.post.title}"