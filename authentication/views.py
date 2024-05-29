from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import *
from .models import *
from django.db.models import Q
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics
from rest_framework_simplejwt.views import TokenRefreshView

# Create your views here.


class ObtainRefreshTokenView(TokenRefreshView):
    permission_classes = (permissions.AllowAny,)


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access.
    """

    def has_permission(self, request, view):
        # Check if the requesting user is authenticated and is an admin
        return request.user and request.user.is_authenticated and request.user.is_staff


@api_view(["POST"])
def register_user(request):
    if request.method == "POST":
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthenticationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)

        if user is not None:
            if user.is_superuser:
                # Assuming you're using JWT for authentication
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "message": "superuser",
                        "access_token": str(refresh.access_token),
                        "refresh_token": str(refresh),
                    }
                )
            else:
                return Response(
                    {
                        "message": "ordinary_user",
                    }
                )
        else:
            return Response(
                {"message": "not_authenticated"}, status=status.HTTP_401_UNAUTHORIZED
            )


@api_view(["GET"])
def userlist(request):
    search_term = request.GET.get("search", "")
    if search_term:
        users = User.objects.filter(
            Q(first_name__icontains=search_term)
            | Q(last_name__icontains=search_term)
            | Q(email__icontains=search_term)
        )
    else:
        users = User.objects.all()

    serializer = UserlistSerializer(users, many=True)
    return Response(serializer.data)


class CustomUserUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserDetailsSerializer

    def get_object(self):
        return self.request.user


class UserDetailsView(generics.RetrieveAPIView):
    serializer_class = UserDetailsSerializer

    def get_object(self):
        return self.request.user


class UserUpdateStatusView(generics.UpdateAPIView):
    print("h1")
    serializer_class = UpdateUserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return User.objects.all()

    def put(self, request, *args, **kwargs):
        print("h2")
        user_id = request.data.get("id")
        print(user_id)
        try:
            instance = self.get_queryset().get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "User status updated", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
