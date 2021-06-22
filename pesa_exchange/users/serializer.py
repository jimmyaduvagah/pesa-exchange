from django.contrib.auth import authenticate
from rest_framework import serializers

from pesa_exchange.users.models import User
from pesa_exchange.wallet.models import Wallet



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'



class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    password = serializers.CharField(max_length=128, min_length=8,
        write_only=True
    )

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        # Use the `create_user` method we wrote earlier to create a new user.
        user = User.objects.create_user(**validated_data)
        wallet = Wallet(owner=user)
        wallet.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # import pdb
        # pdb.set_trace()
        email = data.get('email', None)
        password = data.get('password', None)

        # Raise an exception if an email is not provided.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.' )
        # Raise an exception if a password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.' )

        user = User.objects.get(email=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            'email': user.email,
            'username': user.username,
            'token': user.token
        }