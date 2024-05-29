from rest_framework import serializers, viewsets, permissions
from .models import User
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = "__all__"

    #
    # def create(self, validated_data):
    #     user = User(
    #         username=validated_data['username'],
    #         email=validated_data['email']
    #     )
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user


# class UserUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'first_name', 'last_name', 'mobile', 'gender', 'bio', 'profile_picture', 'status')


class UserlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "mobile",
            "profile_picture",
            "bio",
            "date_joined",
            "last_login",
            "status",
            "gender",
        ]
        partial = True


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "is_active", "status"]
        partial = True
