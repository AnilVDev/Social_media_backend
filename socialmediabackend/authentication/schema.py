import graphene
from graphene_django import DjangoObjectType
from authentication.models import *
from django.contrib.auth import get_user_model
from jwt import decode, InvalidTokenError
from django.conf import settings

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "email", "username","first_name", "last_name", "mobile", "profile_picture", "bio", "date_joined", "last_login", "gender")

class Query(graphene.ObjectType):
    user = graphene.Field(UserType)

    def resolve_user(self, info):
        try:
            auth_header = info.context.headers.get("Authorization")
            token = auth_header.split(" ")[1] if auth_header else None

            if not token:
                raise PermissionError("Token not provided")

            decoded_token = decode(token, settings.SIMPLE_JWT["SIGNING_KEY"], algorithms=["HS256"])
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

# schema = graphene.Schema(query=Query)