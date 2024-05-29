from django.contrib import admin
from post_app.models import *

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    display = '__all__'

admin.site.register(Post, PostAdmin)

class PostMediaAdmin(admin.ModelAdmin):
    display = '__all__'

admin.site.register(PostMedia, PostMediaAdmin)

class LikeAdmin(admin.ModelAdmin):
    display = '__all__'

admin.site.register(Like, LikeAdmin)

class CommentAdmin(admin.ModelAdmin):
    display = '__all__'

admin.site.register(Comment, CommentAdmin)