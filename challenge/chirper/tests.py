from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient

from chirper.models import UserProfile, Chirp

class UserCreateTests(TestCase):
  #
  # Tests
  #
  def test_register_new_valid_user(self):
    """
    Creating a new user should succeed if the username is not unique and
    contains only alphanumeric characters.
    """
    response = self.register_a_user("TestUser")

    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

  def test_register_existing_user(self):
    """
    Attempting to create a duplicate of an existing user should fail, return a
    400 response and let the user know they are trying to create a duplicate.
    """
    # First create a valid user
    create_valid_user = self.register_a_user("TestUser")
    # Then try to create it again
    response = self.register_a_user("TestUser")

    response_data = {
      "username":["This field must be unique."]
    }

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, response_data)

  def test_register_new_user_with_invalid_name(self):
    """
    Attempting to create a new user with invalid chars should fail, return a
    400 response and let the user know they have tried an invalid username.
    """
    response = self.register_a_user("5\t?:|")

    response_data = {
      "username":["Enter a valid username."]
    }

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, response_data)

  #
  # Helper method
  #
  def register_a_user(self, username):
    url = reverse('chirper:register')
    data = {
      "username":username,
      "password":"Password"
    }
    return self.client.post(url, data, format='json')

class UserLoginTests(TestCase):

  # Load some test data
  fixtures = ['DbForTesting.json']

  #
  # Tests
  #
  def test_login_as_existing_user_with_good_password(self):
    """
    Logging in as an existing user should succeed with a 200 response and a JSON
    object containing the relative URL of the redirect.
    """
    response = self.login_as_user("TestUser", "Password")

    redirectUrl = reverse('chirper:home')
    response_data = {
      "redirect":redirectUrl
    }

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data, response_data)

  def test_login_as_existing_user_with_bad_password(self):
    """
    Logging in as an existing user with a bad password should fail with a 400
    response and a direction to re-enter the password.
    """
    response = self.login_as_user("TestUser", "BadPassword")

    response_data = {
      "detail":"Invalid username/password."
    }

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, response_data)

  def test_login_as_nonexistent_user(self):
    """
    Trying to log in a nonexistent user should fail with a 400 response.
    """
    response = self.login_as_user("NoUser", "Password")

    response_data = {
      "detail":"Invalid username/password."
    }

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, response_data)

  #
  # Helper method
  #
  def login_as_user(self, username, password):
    url = reverse('chirper:login')
    data = {
      "username":username,
      "password":password
    }
    return self.client.post(url, data, format='json')

class UserLogoutTests(TestCase):

  # Load some test data
  fixtures = ['DbForTesting.json']

  #
  # Tests
  #
  def test_logout_existing_user(self):
    """
    Logout should return a 200 OK when a logged in user logs out.
    """
    client = APIClient()
    client.login(username='TestUser', password='Password')

    url = reverse('chirper:logout')
    response = client.post(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

  def test_logout_not_logged_in(self):
    """
    Attempting to logout when not actually logged in should return a 403 error.
    """
    client = APIClient()

    url = reverse('chirper:logout')
    response = client.post(url)

    response_data = {
      "detail":"Authentication credentials were not provided."
    }

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    self.assertEqual(response.data, response_data)

class UserDetailTests(TestCase):

  # Load some test data
  fixtures = ['DbForTesting.json']

  #
  # Tests
  #
  def test_user_detail_for_existing_user(self):
    """
    Checking the user detail on an existing user should bring up a list of the
    user's username, join_date, and chirp pks.
    """
    client = APIClient()
    client.login(username='TestUser', password='Password')

    url = reverse('chirper:userDetail', kwargs={'username':'TestUser'})
    response = client.get(url)

    user_id = response.data['id']
    date_joined = response.data['date_joined']
    chirps = response.data['chirps']

    response_data = {
      "id":user_id,
      "username":"TestUser",
      "date_joined":date_joined,
      "chirps":chirps
    }

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data, response_data)

  def test_user_detail_for_nonexistent_user(self):
    """
    Checking the user detial view on a nonexistent user should return a 404
    response.
    """
    client = APIClient()
    client.login(username='TestUser', password='Password')

    url = reverse('chirper:userDetail', kwargs={'username':'NoUser'})
    response = client.get(url)

    response_data = {
      "detail":"Not found."
    }

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    self.assertEqual(response.data, response_data)

  def test_user_detail_anonymous_user(self):
    """
    Attempting to check user details when not logged in should return a 403
    response.
    """
    client = APIClient()

    url = reverse('chirper:userDetail', kwargs={'username':'TestUser'})
    response = client.get(url)

    response_data = {
      "detail":"Authentication credentials were not provided."
    }

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    self.assertEqual(response.data, response_data)

class CreateNewChirp(TestCase):

  # Load some test data
  fixtures = ['DbForTesting.json']

  #
  # Tests
  #
  def test_create_new_valid_chirp_with_logged_in_user(self):
    """
    Creating a new chirp while logged in should succeed and return a 201
    response.
    """
    client = APIClient()
    client.login(username='TestUser', password='Password')

    url = reverse('chirper:home')
    data = {
      "text":"This is a test."
    }
    response = client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

  def test_create_new_valid_chirp_anonymous_user(self):
    """
    Attempting to create a new chirp when not logged in should fail and result
    in a 403 response.
    """
    client = APIClient()

    url = reverse('chirper:home')
    data = {
      "text":"This is a test."
    }
    response = client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

  def test_create_new_invalid_chirp_too_long(self):
    """
    Attempting to create a chirp that is too long should fail and result in a
    400 response.
    """
    client = APIClient()
    client.login(username='TestUser', password='Password')

    url = reverse('chirper:home')
    data = {str([1] * 150)}
    response = client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class FollowUserTests(TestCase):

  # Load some test data
  fixtures = ['DbForTesting.json']

  #
  # Tests
  #
  def test_follow_valid_user(self):
    """
    Following a valid user while logged in should succeed and return a 200
    response.
    """
    response = self.login_and_follow_user("FollowTestUser")

    self.assertEqual(response.status_code, status.HTTP_200_OK)

  def test_follow_user_already_following(self):
    """
    Attempting to follow a user that you are already following should fail and
    return a 400 response.
    """
    response = self.login_and_follow_user("UnfollowTestUser")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  def test_follow_nonexistent_user(self):
    """
    Attempting to follow a user that doesn't exist should fail and return a 404
    response.
    """
    response = self.login_and_follow_user("NoUser")

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

  #
  # Helper method
  #
  def login_and_follow_user(self, user_to_follow):
    client = APIClient()
    client.login(username='TestUser', password='Password')

    url = reverse('chirper:followUser')
    data = {
      "user_to_follow":user_to_follow
    }
    return client.put(url, data, format="json")

class UnfollowUserTests(TestCase):

  # Load some test data
  fixtures = ['DbForTesting.json']

  #
  # Tests
  #
  def test_unfollow_valid_user(self):
    """
    Unfollowing a valid user that you are following should succeed and return a
    200 response.
    """
    response = self.login_and_unfollow_user("UnfollowTestUser")

    self.assertEqual(response.status_code, status.HTTP_200_OK)

  def test_unfollow_user_not_following(self):
    """
    Attempting to unfollow a user that exists, but that you are not following
    should fail and return a 400 response.
    """
    response = self.login_and_unfollow_user("FollowerTestUser")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  def test_unfollow_nonexistent_user(self):
    """
    Attempting to unfollow a user that doesn't exist should fail and return a
    404 response.
    """
    response = self.login_and_unfollow_user("NoUser")

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

  #
  # Helper method
  #
  def login_and_unfollow_user(self, user_to_unfollow):
    client = APIClient()
    client.login(username='TestUser', password='Password')

    url = reverse('chirper:unfollowUser')
    data = {
      "user_to_unfollow":user_to_unfollow
    }
    return client.put(url, data, format="json")
