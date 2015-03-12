from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import timezone

from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from chirper.models import UserProfile, Chirp
from chirper.serializers import UserProfileSerializer, ChirpSerializer


class UserLogin(APIView):
    """
    Provide a POST method to allow registered users to log in to the Chirper
    system. Accepts a JSON object with two name-value pairs: "username" and
    "password".
    """
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            # This format was chosen so that the client side could determine whether
            # to redirect to the home screen rather than forcing a redirect every time
            redirectUrl = reverse('chirper:home')
            response = {'redirect':redirectUrl}

            return Response(response, status.HTTP_200_OK)
        else:
            return Response({'detail':'Invalid username/password.'}, status=status.HTTP_400_BAD_REQUEST)

class UserLogout(APIView):
    """
    Provides a POST method to allow the user to log out of the chirper system.
    POST was chosen to prevent problems with browser pre-fetching.
    """
    def post(self, request, format=None):
        logout(request)
        return Response("OK")

class UserCreate(generics.CreateAPIView):
    """
    Provides a POST method to allow an anonymous user to create a new account.
    Accepts a JSON object with two name-value pairs: "username", and "password".
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (AllowAny,)

class UserList(generics.ListAPIView):
    """
    Provides a GET method to show the list of all users registered in the system.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class UserDetail(generics.RetrieveAPIView):
    """
    Provides a GET method to retrieve a read-only view of a single user. Accepts
    the 'username' in "api/users/username/" as an argument.
    """
    lookup_field = 'username'
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class HomeChirpListCreate(generics.ListCreateAPIView):
    """
    Provides a view to a 'home screen'. GET retrieves a list of chirps from users
    that the current user is following and POST allows the creation of new chirps
    by that user. POST accepts a single JSON name-value pair "text", which has a
    maximum length of 140 characters.
    """
    serializer_class = ChirpSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return Chirp.objects.filter(author__in = self.request.user.following.all())

    def perform_create(self, serializer):
        serializer.save(author = self.request.user, time_posted = timezone.now())

class FollowUser(APIView):
    """
    Provides a PUT method to allow a logged in user to 'follow' other users. This
    will cause the followed users' chirps to appear at the user's 'home' screen.
    PUT accepts one JSON name-value pair: "user_to_follow", which contains the
    username of the user to follow.
    """
    def put(self, request, format=None):
        username = request.data['user_to_follow']
        try:
            user_to_follow = UserProfile.objects.get(username = username)
        except UserProfile.DoesNotExist:
            user_to_follow = None

        if user_to_follow != None:
            if user_to_follow in request.user.following.all():
                return Response("Already following this user.", status.HTTP_400_BAD_REQUEST)

            request.user.following.add(user_to_follow.pk)
            return Response("OK", status.HTTP_200_OK)

        return Response("Not found", status.HTTP_404_NOT_FOUND)

class UnfollowUser(APIView):
    """
    Provides a PUT method to allow a logged in user to 'unfollow' users that they
    have followed. This will cause the now unfollowed users' chirps to disappear
    from the user's 'home' screen. PUT accepts one JSON name-value pair:
    "user_to_unfollow", which contains the username of the user to unfollow.
    """
    def put(self, request, format=None):
        username = request.data['user_to_unfollow']
        try:
            user_to_unfollow = UserProfile.objects.get(username = username)
        except UserProfile.DoesNotExist:
            user_to_unfollow = None

        if user_to_unfollow != None:
            if user_to_unfollow not in request.user.following.all():
                return Response("Not following this user.", status.HTTP_400_BAD_REQUEST)

            request.user.following.remove(user_to_unfollow)
            return Response("OK", status.HTTP_200_OK)

        return Response("Not found", status.HTTP_404_NOT_FOUND)
