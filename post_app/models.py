from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(max_length=500, null=True, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    privacy_settings = models.BooleanField(default=False)
    date_of_memory = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to="posts/%Y/%m/%d/", null=True, blank=True)

    def __str__(self):
        return f"Post by {self.user.email} - {self.id}"

    class Meta:
        ordering = ["-posted_at"]


class PostMedia(models.Model):
    MEDIA_CHOICES = (
        ("image", "Image"),
        ("video", "Video"),
    )
    post = models.ForeignKey(Post, related_name="media", on_delete=models.CASCADE)
    media_type = models.CharField(max_length=10, choices=MEDIA_CHOICES)
    media = models.ImageField(
        upload_to="posts/%Y/%m/%d/",
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "gif"])
        ],
    )
    video = models.FileField(
        upload_to="posts/videos/%Y/%m/%d/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=[".mp4", ".mov", ".avi", ".webm"])
        ],
    )

    def __str__(self):
        return (
            f"{self.media_type} - {self.media.name if self.media else self.video.name}"
        )


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"Like by {self.user.email} on post {self.post.id}"


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.email} on post {self.post.id}"
