import graphene
from graphene_django import DjangoObjectType
from post_app.models import *
from django.contrib.auth import get_user_model
from jwt import decode, InvalidTokenError
from django.conf import settings
from graphene_file_upload.scalars import Upload
from functools import wraps
from django.core.files.storage import default_storage
import uuid

def authenticate_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(" toke ne ")
        info = args[1]
        auth_header = info.context.headers.get("Authorization")
        token = auth_header.split(" ")[1] if auth_header else None

        if token:
            try:
                decoded_token = decode(token, settings.SIMPLE_JWT["SIGNING_KEY"], algorithms=["HS256"])
                user_id = decoded_token["user_id"]
                user = get_user_model().objects.get(id=user_id)
                return func(*args, user_id=user_id, **kwargs)
            except (InvalidTokenError, KeyError, get_user_model().DoesNotExist):
                pass
        raise PermissionError("Invalid token or user not found")
    return wrapper





class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = ("id", "user", "description", 'posted_at', 'privacy_settings', 'date_of_memory','image')


class PostMediaType(DjangoObjectType):
    class Meta:
        model = PostMedia
        fields = ("id", "post", "media_type", "media", "video")

class LikeType(DjangoObjectType):
    class Meta:
        model = Like
        fields = ("id", "user", "post", "liked_at")

class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ("id", "user", "post", "content", "created_at")

class Query(graphene.ObjectType):
    posts = graphene.List(PostType)
    postmedia = graphene.List(PostMediaType)

    def resolve_posts(self, info):
        print("graphql * * * ")
        try:
            # Extract JWT token from the request header
            auth_header = info.context.headers.get("Authorization")
            token = auth_header.split(" ")[1] if auth_header else None

            if not token:
                raise PermissionError("Token not provided")

            # Decode and verify the JWT token
            decoded_token = decode(token, settings.SIMPLE_JWT["SIGNING_KEY"], algorithms=["HS256"])
            user_id = decoded_token["user_id"]
            user = get_user_model().objects.get(id=user_id)

            posts = Post.objects.filter(user=user)

            return posts
        except (InvalidTokenError, KeyError, get_user_model().DoesNotExist):
            raise PermissionError("Invalid token or user not found")



class CreatePostMutation(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID()
        description  = graphene.String(required=False)
        privacy_settings = graphene.Boolean(required=False)
        date_of_memory = graphene.Date(required=False)
        # media = graphene.List(Upload, required=True)
        image = Upload(required=True)

    post = graphene.Field(PostType)

    # @authenticate_user
    # def mutate(self,info, user_id, description, date_of_memory, media, privacy_settings = False):
    #     user = get_user_model().objects.get(id= user_id)
    #     print(description,date_of_memory,media,privacy_settings)
    #     post = Post.objects.create(
    #         user = user,
    #         description = description,
    #         privacy_settings = privacy_settings,
    #         date_of_memory = date_of_memory
    #     )
    #
    #     if media:
    #         for upload in media:
    #             media_type = upload.content_type.split("/")[0]
    #             if media_type == "image":
    #                 media_obj = PostMedia.objects.create(post=post, media_type="image", media=media.file)
    #             elif media_type == "video":
    #                 media_obj = PostMedia.objects.create(post=post, media_type="video", video=media.file)
    #             else:
    #                 raise Exception("Invalid media type")
    #
    #     return  CreatePostMutation(post=post)

    @authenticate_user
    def mutate(self, info, user_id, description, image, privacy_settings=False, date_of_memory=None):
        try:
            user = get_user_model().objects.get(id=user_id)
            print("image --", description,image)
            # file_name = str(uuid.uuid4()) + '_' + image.name
            # with default_storage.open(file_name, 'wb+') as f:
            #     for chunk in image.chunks():
            #         f.write(chunk)

            post = Post(
                user=user,
                description=description,
                privacy_settings=privacy_settings,
                date_of_memory=date_of_memory,
                image=image
            )
            post.save()
            return CreatePostMutation(post=post)
        except Exception as e:
            return CreatePostMutation(post=None)


class UpdatePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        user_id = graphene.ID()
        description = graphene.String()
        privacy_settings = graphene.String()
        date_of_memory = graphene.String()
        media = Upload()

    post = graphene.Field(PostType)

    def mutate(self, info, id, user_id, description, privacy_settings, date_of_memory, media):
        user = get_user_model().objects.get(id=user_id)
        post = Post.objects.get(id=id)

        if post.user != user:
            raise PermissionError("User not authorized to update this post")

        post.description = description
        post.privacy_settings = privacy_settings
        post.date_of_memory = date_of_memory

        if media:
            PostMedia.objects.filter(post=post).delete()
            media_type = media.content_type.split("/")[0]
            if media_type == "image":
                media_obj = PostMedia.objects.create(post=post, media_type="image", media=media.file)
            elif media_type == "video":
                media_obj = PostMedia.objects.create(post=post, media_type="video", video=media.file)
            else:
                raise Exception("Invalid media type")

        post.save()

        return UpdatePostMutation(post=post)

class DeletePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        user_id = graphene.ID()

    post = graphene.Field(PostType)

    def mutate(self, info, id, user_id):
        user = get_user_model().objects.get(id=user_id)
        post = Post.objects.get(id=id)

        if post.user != user:
            raise PermissionError("User not authorized to delete this post")

        post.delete()

        return DeletePostMutation(post=post)

class Mutation(graphene.ObjectType):
    create_post = CreatePostMutation.Field()
    update_post = UpdatePostMutation.Field()
    delete_post = DeletePostMutation.Field()






