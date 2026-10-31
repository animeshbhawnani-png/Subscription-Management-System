import re
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()

PASSWORD_RE = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9]).{9,}$')


def _validate_strong_password(value):
    """Upper + lower + special char + min 8 chars (9+ with all three classes)."""
    if not PASSWORD_RE.match(value):
        raise serializers.ValidationError(
            "Password must be at least 8 characters and contain uppercase, "
            "lowercase, and a special character."
        )
    validate_password(value)  # also runs Django's built-in validators
    return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password")

    def validate_password(self, value):
        return _validate_strong_password(value)

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role="customer",
        )


class StaffCreateSerializer(serializers.ModelSerializer):
    """Admin-only: create a staff account."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password")

    def validate_password(self, value):
        return _validate_strong_password(value)

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role="staff",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "role", "date_joined")
        read_only_fields = fields


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    uid = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        return _validate_strong_password(value)

