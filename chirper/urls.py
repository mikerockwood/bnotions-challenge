from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from chirper import views

urlpatterns = [
  url(r'^login/$', views.UserLogin.as_view(), name='login'),
  url(r'^logout/$', views.UserLogout.as_view(), name='logout'),
  url(r'^register/$', views.UserCreate.as_view(), name='register'),
  url(r'^home/$', views.HomeChirpListCreate.as_view(), name='home'),
  url(r'^users/$', views.UserList.as_view(), name='userList'),
  url(r'^users/(?P<username>\w+)/$', views.UserDetail.as_view(), name='userDetail'),
  url(r'^follow/$', views.FollowUser.as_view(), name='followUser'),
  url(r'^unfollow/$', views.UnfollowUser.as_view(), name='unfollowUser'),
]
