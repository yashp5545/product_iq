from rest_framework.authentication import get_authorization_header
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSerializer
from .authentication import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token
from .models import User


def isAuth(func_view):
    def wrapper(request, *args, **kwargs):
        auth = get_authorization_header(request).split()
        if (auth and len(auth) == 2):
            if (auth[0].decode().lower() != 'bearer'):
                return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                user_id = decode_access_token(auth[1])
                user = User.objects.get(id=user_id)

                if (not user):
                    return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
                serializer = UserSerializer(user)
                return func_view(request, serializer.data, *args, **kwargs)
            except Exception as e:
                return Response({'Internal Server Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    return wrapper
