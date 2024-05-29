from django.contrib import admin
from post_app.models import *


# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'description',
        'posted_at',
        'privacy_settings',
        'date_of_memory',
        'image'
    ]

admin.site.register(Post, PostAdmin)


class PostMediaAdmin(admin.ModelAdmin):
    display = "__all__"


admin.site.register(PostMedia, PostMediaAdmin)


class LikeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'post',
        'liked_at'
    ]


admin.site.register(Like, LikeAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'post',
        'content',
        'created_at'
    ]


admin.site.register(Comment, CommentAdmin)
