from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from account.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1.00)],
    )
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_canceled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def current_amount(self):
        return self.donations.aggregate(
            total=models.Sum('amount')
        )['total'] or 0.00

    @property
    def funding_percentage(self):
        if self.target_amount > 0:
            return round((self.current_amount / self.target_amount) * 100, 2)
        return 0.00

    @property
    def can_be_canceled(self):
        return self.funding_percentage < 25

    @property
    def average_rating(self):
        avg = self.ratings.aggregate(avg=models.Avg('value'))['avg']
        return round(avg, 2) if avg else 0.00
    
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"


class Donation(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='donations')
    post = models.ForeignKey('Post',on_delete=models.CASCADE,related_name='donations')
    amount = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(1.00)])
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} donated ${self.amount} to {self.post.title}"
    
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='ratings')
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
    def __str__(self):
        return f"{self.user.username} rated {self.post.title} as {self.value}"