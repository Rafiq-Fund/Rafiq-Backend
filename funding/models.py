from django.db import models
from django.core.validators import MinValueValidator
from account.models import User

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    # Add these fields for funding functionality
    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1.00)],
        help_text="Funding goal amount"
    )
    deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional funding deadline"
    )

    def __str__(self):
        return self.title
    
    # Property to calculate current funding progress
    @property
    def current_amount(self):
        return self.donations.aggregate(  # type: ignore
            total=models.Sum('amount')
        )['total'] or 0.00
    
    # Property to calculate funding percentage
    @property
    def funding_percentage(self):
        if self.target_amount > 0:
            return round((self.current_amount / self.target_amount) * 100, 2) # type: ignore
        return 0.00
    
class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='post_images/')
    def __str__(self):
        return self.post.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}"

class Donation(models.Model):
    user = models.ForeignKey(
        User,
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