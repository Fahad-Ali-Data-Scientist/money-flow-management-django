from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'authentication/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@csrf_protect
def register_view(request):
    if request.user.is_authenticated and request.user.is_admin:
        if request.method == 'POST':
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            role = request.POST.get('role')
            password = request.POST.get('password')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered')
                return render(request, 'authentication/register.html')
            
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            
            messages.success(request, f'Account created successfully for {email}')
            return redirect('user_list')
        
        return render(request, 'authentication/register.html')
    else:
        return redirect('login')

@api_view(['POST'])
@permission_classes([AllowAny])
def token_obtain_pair(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = authenticate(email=email, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
            }
        })
    else:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@login_required
def user_list(request):
    if not request.user.is_admin:
        return redirect('dashboard')
    
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'authentication/user_list.html', {'users': users})
