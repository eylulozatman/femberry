from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import *
from .models import *
import json
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import OuterRef, Exists


def index(request):
    return render(request, 'main/index.html')

def contact_view(request):
    return render(request, 'main/contact.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('homepage')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')



@login_required
def homepage_view(request):
    user = request.user
    user_detail = get_user_details(user)
    post_data = get_posts(request)  # Get all post data
    friendrequests = get_friend_request_view(request)
    friends = get_all_friends_view(request)
    user_pref, created = UserPref.objects.get_or_create(user=user)
    
    return render(request, 'main/homepage.html', {
        'user': user,
        'user_detail': user_detail,
        'posts': post_data,
        'friendrequests': friendrequests,
        'friends': friends,
        'user_pref': user_pref 
    })


def poll_page_view(request):
    return redirect('poll')

@login_required
def homepage_targetpost_view(request, matching_posts=None):
    user = request.user
    user_detail = get_user_details(user)
    if matching_posts is None:
        post_data = get_posts(request)  # Tüm post verilerini al
    else:
        post_data = matching_posts

    friendrequests = get_friend_request_view(request)
    friends = get_all_friends_view(request)

    return render(request, 'main/homepage.html', {
        'user': user,
        'user_detail': user_detail,
        'posts': post_data,
        'friendrequests': friendrequests,
        'friends': friends
    })


def get_user_details(user):
    try:
        return UserDetail.objects.get(user=user)
    except UserDetail.DoesNotExist:
        return None
    

@login_required
def edit_user_profile(request):
    user = request.user
    try:
        user_detail = UserDetail.objects.get(user=user)
    except UserDetail.DoesNotExist:
        user_detail = UserDetail(user=user)

    if request.method == 'POST':
        form = UserDetailForm(request.POST, request.FILES, instance=user_detail)
        if form.is_valid():
            # Boş olmayan alanları filtrele
            cleaned_data = form.cleaned_data
            filled_fields = {k: v for k, v in cleaned_data.items() if v}
            
            # Veritabanındaki kullanıcı detaylarını güncelle
            for field, value in filled_fields.items():
                setattr(user_detail, field, value)
            user_detail.save()

            messages.success(request, 'Profile updated successfully.')
            return redirect('homepage')
    else:
        form = UserDetailForm(instance=user_detail)

    return render(request, 'main/editprofile.html', {'form': form})


@login_required
def new_post_send_view(request):
    if request.method == 'POST':
        title = request.POST.get('title') 
        Post.objects.create(user=request.user, title=title)
        return redirect('homepage')

@login_required
def photo_post_send_view(request):
 if request.method == 'POST':
        title = request.POST.get('title')
        photo = request.FILES.get('photo')
        Post.objects.create(user=request.user, title=title, photo_data=photo)
        return redirect('homepage')
 

@login_required
def get_posts(request, filter_criteria=None):
    current_user = request.user

    # Get or create user preferences
    user_pref, created = UserPref.objects.get_or_create(user=current_user)
    
    # Eğer kullanıcı sadece arkadaşlarının postlarını görmek istiyorsa
    if user_pref.postsFromFriends:
        # Arkadaşlar için Subquery kullanarak daha verimli bir sorgu yapın
        friend_ids = Friend.objects.filter(user=current_user, friend=OuterRef('user_id'))
        posts = Post.objects.filter(Exists(friend_ids)).order_by('-post_date')[:50]
        if not posts.exists():
            posts = [
                Post(
                    user=current_user,  
                    title="Start adding friends!",
                    post_date=timezone.now(),
                    photo_data=None
                )
            ]

    elif filter_criteria:
        posts = Post.objects.filter(**filter_criteria).order_by('-post_date')[:50]
    else:
        posts = Post.objects.all().order_by('-post_date')[:50]

    # Kullanıcının beğendiği postları ID listesi olarak alın
    liked_post_ids = LikePost.objects.filter(user_like=current_user).values_list('post_like_id', flat=True)

    post_data = [{
        'id': post.id,
        'title': post.title,
        'post_date': format_post_date(post.post_date),
        'photo_data': post.photo_data.url if post.photo_data else None,
        'user': {'username': post.user.username},
        'is_owner': post.user == current_user,
        'is_liked': post.id in liked_post_ids  # Beğenme durumu
    } for post in posts]

    return post_data

@login_required
def update_userPref_view(request):
    if request.method == 'POST':
        try:
            current_user = request.user

            # Get or create user preferences
            user_pref, created = UserPref.objects.get_or_create(user=current_user)

            # Toggle the postsFromFriends field
            user_pref.postsFromFriends = not user_pref.postsFromFriends
            user_pref.save()

            # Return a JSON response with success
            return JsonResponse({'success': True, 'redirect': 'homepage'}, status=200)
        except Exception as e:
            # Return JSON response on error
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        # Handle invalid request method
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def format_post_date(post_date):
    now = timezone.now()
    difference = now - post_date

    if difference.days == 0:
        if difference.seconds < 3600:
            return 'Just now'
        elif difference.seconds < 7200:
            return '1 hour ago'
        else:
            return '{} hours ago'.format(difference.seconds // 3600)
    elif difference.days == 1:
        return 'Yesterday'
    elif difference.days < 7:
        return '{} days ago'.format(difference.days)
    else:
        return post_date.strftime('%Y-%m-%d')


@login_required
def delete_one_post_view(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id, user=request.user)
        post.delete()
        return redirect('homepage')
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def edit_one_post_view(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        new_text = request.POST.get('newText')

        post = get_object_or_404(Post, id=post_id)

        # Check if the logged-in user is the owner of the post
        if post.user != request.user:
            return JsonResponse({'error': 'Invalid request'}, status=403)  # Use 403 Forbidden

        post.title = new_text
        post.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def search_person_view(request):
    if request.method == 'POST':
        target_word = request.POST.get('searchQuery', '')
        matching_users = User.objects.filter(username__icontains=target_word)
        matching_data = []

        for user in matching_users:
            friend_request = FriendRequest.objects.filter(
                user=request.user,
                requested=user
            ).first()

            if friend_request:
                status = friend_request.status
            else:
                status = 'none'  # Indicates no friend request exists

            matching_data.append({
                'username': user.username,
                'status': status
            })

        data = {
            'matching_users': matching_data,
        }
        return JsonResponse(data)
 
@login_required
def send_friendship_view(request, username):
    if request.method == 'POST':
        try:
            user = User.objects.get(username=username)
            # Check if there is an existing friend request
            existing_request = FriendRequest.objects.filter(user=request.user, requested=user).exists()
            if not existing_request:
                FriendRequest.objects.create(user=request.user, requested=user)
            return JsonResponse({'status': 'success'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def get_friend_request_view(request):
    user = request.user
    friend_requests = FriendRequest.objects.filter(requested=user, status='waiting')
    return friend_requests

@login_required
def get_all_friends_view(request):
    user = request.user
    friends = Friend.objects.filter(user=user)
    friend_list = []
    for friend in friends:
        friend_user = friend.friend
        friend_list.append({
            'username': friend_user.username,
            'first_name': friend_user.first_name,
            'last_name': friend_user.last_name,
        })
    return friend_list


@login_required
def respond_to_request_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request_id = data.get('request_id')
            action = data.get('action')
            if not request_id or not action:
                return JsonResponse({'success': False, 'error': 'Missing parameters'}, status=400)
                
            friend_request = FriendRequest.objects.get(id=request_id)
            if action == 'accepted':
                friend_request.status = 'accepted'
                Friend.objects.create(user=request.user, friend=friend_request.user)
                Friend.objects.create(user=friend_request.user, friend=request.user)
            elif action == 'rejected':
                friend_request.status = 'rejected'
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)
            
            friend_request.save()
            return JsonResponse({'success': True})
        except FriendRequest.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Request does not exist'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
def search_post_view(request):
    if request.method == 'POST':
        target_word = request.POST.get('searchQuery', '')
        matching_posts = get_posts(request, filter_criteria={'title__icontains': target_word})
        return homepage_targetpost_view(request, matching_posts)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def like_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Check if the user already liked the post
    if LikePost.objects.filter(user_like=request.user, post_like=post).exists():
        # If the like already exists, return a JSON response indicating the post is already liked
        return JsonResponse({'status': 'already_liked'}, status=200)
    
    # Otherwise, create a new like
    LikePost.objects.create(user_like=request.user, post_like=post)
      
    return JsonResponse({'status': 'liked'}, status=200)

@login_required
def unlike_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Check if the user has liked the post
    like = LikePost.objects.filter(user_like=request.user, post_like=post)
    
    if like.exists():
        like.delete()
    
    return JsonResponse({'status': 'unliked'}, status=200)
