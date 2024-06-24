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



def index(request):
    return render(request, 'main/index.html')

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
    posts = all_post_view(request)  # Tüm post verilerini al
    postdata = json.loads(posts.content.decode('utf-8'))  # JSON verisini dönüştür
    friendrequests = get_friend_request_view(request)
    friends = get_all_friends_view(request)
    return render(request, 'main/homepage.html', {
        'user': user, 
        'user_detail': user_detail, 
        'posts': postdata, 
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
def all_post_view(request):
    current_user = request.user
    posts = Post.objects.all().order_by('-post_date')[:50]
    post_data = [{
        'id': post.id,
        'title': post.title,
        'post_date': format_post_date(post.post_date),
        'photo_data': post.photo_data.url if post.photo_data else None,
        'user': {'username': post.user.username},
        'is_owner': post.user == current_user
    } for post in posts]
    return JsonResponse(post_data, safe=False)


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
def send_friendship_view(request):
    if request.method == 'GET':
        username = request.GET.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                # Check if there is an existing friend request
                existing_request = FriendRequest.objects.filter(user=request.user, requested=user).exists()
                if not existing_request:
                    FriendRequest.objects.create(user=request.user, requested=user)
            except User.DoesNotExist:
                pass
    return JsonResponse({'status': 'success'})  # Return success status

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
        data = json.loads(request.body)
        request_id = data.get('request_id')
        action = data.get('action')
        try:
            friend_request = FriendRequest.objects.get(id=request_id)
            if action == 'accepted':
                friend_request.status = 'accepted'
                Friend.objects.create(user=request.user, friend=friend_request.user)
                Friend.objects.create(user=friend_request.user, friend=request.user)
            elif action == 'rejected':
                friend_request.status = 'rejected'
            friend_request.save()
            return JsonResponse({'success': True})
        except FriendRequest.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Request does not exist'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})