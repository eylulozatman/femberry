from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contact/', views.contact_view, name='contact'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('homepage/', views.homepage_view, name='homepage'),
    path('edit-user-profile/', views.edit_user_profile, name='edit_user_profile'),
    path('new-post-send/', views.new_post_send_view, name='new-post-send'),
    path('photo-post-send/', views.photo_post_send_view, name='photo-post-send'),
    path('delete-one-post/', views.delete_one_post_view, name='delete-one-post'),
    path('edit-one-post/',views.edit_one_post_view, name='edit-one-post'),
    path('search-post/', views.search_post_view, name='search-post'),
    path('search-person/', views.search_person_view, name='search-person'),
    path('send-friendship/<str:username>/', views.send_friendship_view, name='send-friendship'),
    path('get-all-friendRequests',views.get_friend_request_view, name='get-all-friendRequests'),
    path('get-all-friends',views.get_all_friends_view, name='get-all-friends' ),
    path('respond-friend-request',views.respond_to_request_view, name='respond-friend-request' ),
    path('poll-page/',views.poll_page_view,name = 'poll-page'),
    path('like-post/<int:post_id>/', views.like_post_view, name='like_post'),
    path('unlike-post/<int:post_id>/', views.unlike_post_view, name='unlike_post'),
    path('update-user-pref/',views.update_userPref_view,name = 'update-user-pref'),
    path('visit-user/<int:friendId>/', views.visit_user_view, name='visit_user'),
    path('delete-friend/<int:friendId>/', views.delete_friend_view, name='delete-friend'),


]
