import graphene
from graphene_django import DjangoObjectType
from authentication.models import *
from django.contrib.auth import get_user_model
from jwt import decode, InvalidTokenError
from django.conf import settings
from functools import wraps
from django.db.models import Q
from graphql import GraphQLError


def authenticate_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(" toke ne ")
        info = args[1]
        auth_header = info.context.headers.get("Authorization")
        token = auth_header.split(" ")[1] if auth_header else None

        if token:
            try:
                decoded_token = decode(
                    token, settings.SIMPLE_JWT["SIGNING_KEY"], algorithms=["HS256"]
                )
                user_id = decoded_token["user_id"]
                user = get_user_model().objects.get(id=user_id)
                return func(*args, user_id=user_id, **kwargs)
            except (InvalidTokenError, KeyError, get_user_model().DoesNotExist):
                pass
        raise PermissionError("Invalid token or user not found")

    return wrapper


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "mobile",
            "profile_picture",
            "bio",
            "date_joined",
            "last_login",
            "gender",
        )


class FollowType(DjangoObjectType):
    class Meta:
        model = Follow
        fields = ("id", "follower", "following", "created_at")


class FollowResult(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()


class Query(graphene.ObjectType):
    user = graphene.Field(UserType)
    followers = graphene.List(UserType, id=graphene.Int())
    following = graphene.List(UserType, id=graphene.Int())
    friend_followers = graphene.List(UserType, id=graphene.ID())
    friend_following = graphene.List(UserType, id=graphene.ID())
    isFollowing = graphene.Boolean(following_id=graphene.ID(required=True))

    def resolve_user(self, info):
        try:
            auth_header = info.context.headers.get("Authorization")
            token = auth_header.split(" ")[1] if auth_header else None

            if not token:
                raise PermissionError("Token not provided")

            decoded_token = decode(
                token, settings.SIMPLE_JWT["SIGNING_KEY"], algorithms=["HS256"]
            )
            user_id = decoded_token["user_id"]

            # user = get_user_model().objects.get(id=user_id)
            user = User.objects.get(pk=user_id)

            return user

        except InvalidTokenError:
            raise PermissionError("Invalid token")
        except KeyError:
            raise PermissionError("Token format is invalid")
        except get_user_model().DoesNotExist:
            raise PermissionError("User not found")

    @authenticate_user
    def resolve_followers(self, info, user_id):
        try:
            user = User.objects.get(id=user_id)
            followed_users = [follow.follower for follow in user.followers.all()]
            return followed_users
        except User.DoesNotExist:
            raise GraphQLError("User not found.")

    @authenticate_user
    def resolve_following(self, info, user_id):
        try:
            user = User.objects.get(id=user_id)
            following_users = [follow.following for follow in user.following.all()]
            return following_users
        except User.DoesNotExist:
            raise GraphQLError("User not found")

    @authenticate_user
    def resolve_friend_followers(self, info, user_id, id):
        try:
            user = User.objects.get(id=id)
            followed_users = [follow.follower for follow in user.followers.all()]
            return followed_users
        except User.DoesNotExist:
            raise GraphQLError("User not found.")

    @authenticate_user
    def resolve_friend_following(self, info, user_id, id):
        try:
            user = User.objects.get(id=id)
            following_users = [follow.following for follow in user.following.all()]
            return following_users
        except User.DoesNotExist:
            raise GraphQLError("User not found")

    @authenticate_user
    def resolve_isFollowing(self, info, user_id, following_id):
        try:
            follower_user = User.objects.get(id=user_id)
            following_user = User.objects.get(id=following_id)

            is_following = Follow.objects.filter(
                follower=follower_user, following=following_user
            ).exists()
            return is_following
        except User.DoesNotExist:
            raise GraphQLError("User not found.")


class SearchUsersMutation(graphene.Mutation):
    class Arguments:
        search = graphene.String(required=True)

    matching_users = graphene.List(UserType)

    @authenticate_user
    def mutate(self, info, user_id, search):
        print(search)
        user = get_user_model().objects.get(id=user_id)
        matching_users = User.objects.filter(
            Q(username__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search),
        )
        matching_users = matching_users.filter(
            is_active=True, status="active", is_superuser=False
        ).exclude(id=user.id)
        return SearchUsersMutation(matching_users=matching_users)


class AddFollowerMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    Output = FollowResult

    @authenticate_user
    def mutate(self, info, user_id, id):
        try:
            current_user = User.objects.get(id=user_id)
            user_to_follow = User.objects.get(id=id)
            if user_to_follow != current_user:
                Follow.objects.create(follower=current_user, following=user_to_follow)
                return FollowResult(success=True, message="Successfully followed user.")
            else:
                return FollowResult(success=False, message="Cannot follow yourself.")
        except User.DoesNotExist:
            return FollowResult(success=False, message="User not found.")


class RemoveFollowerMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    Output = FollowResult

    @authenticate_user
    def mutate(self, info, user_id, id):
        try:
            current_user = User.objects.get(id=user_id)
            user_to_unfollow = User.objects.get(id=id)
            follow_instance = Follow.objects.get(
                follower=current_user, following=user_to_unfollow
            )
            follow_instance.delete()
            return FollowResult(success=True, message="Successfully unfollowed user.")
        except User.DoesNotExist:
            return FollowResult(success=False, message="User not found.")
        except Follow.DoesNotExist:
            return FollowResult(
                success=False, message="You are not following this user."
            )


class Mutation(graphene.ObjectType):
    search_users = SearchUsersMutation.Field()
    add_follower = AddFollowerMutation.Field()
    remove_follower = RemoveFollowerMutation.Field()
