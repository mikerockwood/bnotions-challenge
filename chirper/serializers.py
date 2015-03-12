from rest_framework import serializers
from django.utils import timezone
from chirper.models import UserProfile, Chirp

class UserProfileSerializer(serializers.ModelSerializer):
    # Chirps have a reverse relationship to users, so we need to
    # explicitly load the user's chirps
    chirps = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'password', 'date_joined', 'chirps')
        read_only_fields = ('date_joined',)
        extra_kwargs = {
            'password' : {'write_only': True},
        }

    def create(self, validated_data):
        """
        Overridden so that the password field is properly hashed on user creation.
        """
        user = super(UserProfileSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user

class ChirpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chirp
        fields = ('author', 'time_posted', 'text')
        read_only_fields = ('author', 'time_posted',)
