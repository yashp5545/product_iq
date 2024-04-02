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


@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    print(request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    user = User.objects.filter(username=request.data['username']).first()
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(request.data['password']):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    user.last_login = datetime.now()
    user.save()

    responce = Response()
    responce.set_cookie('refressToken', refresh_token, httponly=True)
    responce.data = {
        'token': access_token
    }

    return responce


@api_view(['GET'])
def get_user(request):
    auth = get_authorization_header(request).split()
    print(auth)

    if auth and len(auth) == 2:
        if auth[0].decode().lower() != 'bearer':
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_id = decode_access_token(auth[1])
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def refress_token(request):
    refresh_token = request.COOKIES.get('refressToken')
    print(request.COOKIES)
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
