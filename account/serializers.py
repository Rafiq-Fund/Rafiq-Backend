from account.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.core.validators import RegexValidator

class LoginSerializer(TokenObtainPairSerializer):
     def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid email or password.")

        if not user.verified:
            raise AuthenticationFailed("Account is not activated. Please check your email.")

        data = super().validate(attrs)
        return data
     @classmethod
     def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(
        required=True,
        validators=[
            RegexValidator(
                regex=r'^01[0125][0-9]{8}$',
                message="Phone number must be a valid Egyptian mobile number."
            )
        ]
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password", "password2", "address", "birth_date", "phone", "profile_picture"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.verified = False 
        user.set_password(password)
        user.save()
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "profile_picture", "bio", "phone" , "address", "birth_date"
        ]
        read_only_fields = ["id", "username", "email"]

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "profile_picture", "bio", "address", "birth_date", "phone"]
        read_only_fields = ["email"]
    
    def validate_phone(self, value):
        if not value:
            return value
        phone_validator = RegexValidator(
            regex=r'^01[0125][0-9]{8}$',
            message="Phone number must be a valid Egyptian mobile number."
        )
        phone_validator(value)
        return value

