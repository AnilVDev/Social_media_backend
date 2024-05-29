from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import TokenError

from graphene_django.middleware import DjangoMiddleware


User = get_user_model()


class AuthenticationMiddleware(DjangoMiddleware):

    def resolve(self, next, root, info, **kwargs):
        # Extract token from request headers (adjust based on your setup)
        token = info.context.get("HTTP_AUTHORIZATION", None)
        if not token or not token.startswith("Bearer "):
            raise AuthenticationFailed("Missing or invalid authorization header")

        try:
            # Decode and verify the token using SimpleJWT
            decoded_data = TokenError.decode(token[7:])  # Remove 'Bearer ' prefix
            user = User.objects.get(pk=decoded_data["user_id"])
            info.context["user"] = user
        except TokenError as e:
            raise AuthenticationFailed(str(e))

        return next(root, info, **kwargs)
