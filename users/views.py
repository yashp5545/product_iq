# Inside views.py

import datetime
from django.http import HttpRequest
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import get_authorization_header

from .models import PRODUCT_EXP_CHOICES, User
from .serializers import UserSerializer
from .authentication import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token
from .isAuth import isAuth


@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    print(request.data)
    if serializer.is_valid():
        serializer.save()
        access_token = create_access_token(serializer.data['id'])
        refresh_token = create_refresh_token(serializer.data['id'])
        responce = Response()
        responce.set_cookie('refressToken', refresh_token, httponly=True)
        responce.data = {
            'token': access_token,
            'name': serializer.data['name'],
            'email': serializer.data['email'],
            'username': serializer.data['username'],
            'product_exp': serializer.data['product_exp'],
            'phone_number': serializer.data['phone_number'],
            'job_title': serializer.data['job_title'],
            'company': serializer.data['company_or_institiution'],
        }
        return responce
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    user = User.objects.filter(username=request.data['username']).first()
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(request.data['password']):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    user.last_login = datetime.datetime.now()
    user.save()

    responce = Response()
    responce.set_cookie('refressToken', refresh_token, httponly=True)
    responce.data = {
        'token': access_token,
        'name': user.name,
        'email': user.email,
        'username': user.username,
        'product_exp': user.product_exp,
        'phone_number': user.phone_number,
        'job_title': user.job_title,
        'company': user.company_or_institiution,
    }

    return responce


@api_view(['GET'])
@isAuth
def get_user(request, user):
    return Response(user)


@api_view(['GET'])
def refress_token(request):
    refresh_token = request.COOKIES.get('refressToken')
    if not refresh_token:
        return Response({'error': 'Invalid token 1'}, status=status.HTTP_401_UNAUTHORIZED)

    user_id = decode_refresh_token(refresh_token)
    if user_id is None:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

    user = User.objects.get(id=user_id)
    access_token = create_access_token(user.id)
    return Response({'token': access_token})


@api_view(['POST'])
def logout(request):
    responce = Response()
    responce.delete_cookie('refressToken')
    responce.data = {
        'message': 'success'
    }
    return responce


@api_view(['POST'])
def update_user(request):
    auth = get_authorization_header(request).split()
    print(auth)

    if auth and len(auth) == 2:
        if auth[0].decode().lower() != 'bearer':
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_id = decode_access_token(auth[1])
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PUT'])
@isAuth
def add_referred_by(request, user):
    user = User.objects.get(id=user['id'])
    user_refered_by = User.objects.get(username=request.data['username'])
    if (user_refered_by == None):
        return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
    if (user_refered_by == user):
        return Response({'error': 'You cannot refer yourself'}, status=status.HTTP_400_BAD_REQUEST)
    if (user.refered_by):
        return Response({'error': 'Referral already added!'}, status=status.HTTP_400_BAD_REQUEST)
    user.refered_by = user_refered_by
    user.save()
    return Response({'message': 'success', 'user': user.username, 'refered_by': user_refered_by.username})


@api_view(["POST"])
def forgot_password(request):
    email = request.data.get("email")
    if not email:
        return Response({
            "error": "Email is required for password reset",
        }, status=400)


@api_view(["GET"])
def get_product_exp_types(request):
    return Response({"PRODUCT_EXPERIENCE": [product_exp.value for product_exp in PRODUCT_EXP_CHOICES]})
