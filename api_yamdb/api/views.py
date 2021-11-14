from rest_framework import viewsets, filters, permissions
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from django.core.mail import send_mail

from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import User

from django.utils.crypto import get_random_string
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .serializers import CreateUserSerializer
from .permissions import IsAdmin
from .serializers import (
    CreateUserSerializer,
    CreateUserInBaseSerializer,
    CreateTokenSerializer,
    UserPatchMeSerializer
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'access': str(refresh.access_token)
    }


def send_mail_with_code(confirmation_code, email):
    send_mail(
        'Код регистрации',
        f'{confirmation_code}',
        'api_yamdb@mail.com',
        [f'{email}'],
        fail_silently=False,
    )


@api_view(['POST'])
def create_user(request):

    """Добавить эдакое хэширование кода."""

    if request.data.get('username') == 'me':
        return Response('oh no! not me!', status=status.HTTP_400_BAD_REQUEST)

    serializer = CreateUserInBaseSerializer(data=request.data)
    email = request.data.get('email')
    confirmation_code = get_random_string(10)
    code = confirmation_code
    if serializer.is_valid():
        serializer.save(confirmation_code=code)
        send_mail_with_code(confirmation_code, email)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_token(request):

    """Часть if перенести в сериализаторы."""

    serializer = CreateTokenSerializer(data=request.data)

    if serializer.is_valid():

        if request.data.get('username') or request.data == {}:
            pass
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        request_code = request.data.get('confirmation_code')
        user = get_object_or_404(User, username=request.data.get('username'))
        user_code = user.confirmation_code

        if request_code == user_code:
            token = get_tokens_for_user(user)
            return Response(token, status=status.HTTP_200_OK)
        else:
            return Response('failed', status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def get_or_patch_user(request):
    if request.method == 'GET':
        user = get_object_or_404(User, username=request.user.username)
        data = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "bio": user.bio,
            "role": user.role
        }
        return Response(data, status=status.HTTP_200_OK)

    if request.method == 'PATCH':
        user = get_object_or_404(User, username=request.user.username)
        serializer = UserPatchMeSerializer(
            user,
            data=request.data,
            partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    permission_classes = (permissions.IsAuthenticated, IsAdmin,)
    serializer_class = CreateUserSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
