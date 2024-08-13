from django.db import models
from django.contrib.auth.models import User


class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profilephoto = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)


class UserPref(models.Model):
    user = models.ForeignKey(User, related_name='user_prefs', on_delete=models.CASCADE)
    postsFromFriends = models.BooleanField(default=False)

class Poll(models.Model):
    owner = models.ForeignKey(User, related_name='polls', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    options = models.JSONField() 


class PollAnswer(models.Model):
    poll = models.ForeignKey(Poll, related_name='answers', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='poll_answers', on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)  


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    post_date = models.DateTimeField(auto_now_add=True)
    photo_data = models.ImageField(upload_to='photos/', blank=True, null=True)

class FriendRequest(models.Model):
    user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    requested = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)

class Friend(models.Model):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friends_with', on_delete=models.CASCADE)


class LikePost(models.Model):
    user_like = models.ForeignKey(User, related_name='user_like', on_delete=models.CASCADE)
    post_like = models.ForeignKey(Post, related_name='post_like', on_delete=models.CASCADE)
