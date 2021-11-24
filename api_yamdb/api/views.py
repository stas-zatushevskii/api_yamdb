from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import User

from api_yamdb.settings import EMAIL_FROM

from .permissions import IsAdmin
from .serializers import (CreateTokenSerializer, CreateUserInBaseSerializer,
                          CreateUserSerializer)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'access': str(refresh.access_token)
    }


def send_mail_with_code(confirmation_code, email):
    send_mail(
        'Код регистрации',
        confirmation_code,
        EMAIL_FROM,
        [email],
        fail_silently=False,
    )


@api_view(['POST'])
def create_user(request):

    if request.data.get('username') == 'me':
        return Response('oh no! not me!', status=status.HTTP_400_BAD_REQUEST)

    serializer = CreateUserInBaseSerializer(data=request.data)
    email = request.data.get('email')
    confirmation_code = get_random_string(10)
    code = confirmation_code
    serializer.is_valid(raise_exception=True)
    serializer.save(confirmation_code=code)
    send_mail_with_code(confirmation_code, email)
    return Response(serializer.data)


@api_view(['POST'])
def create_token(request):

    serializer = CreateTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if not (request.data.get('username') or request.data == {}):
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    request_code = request.data.get('confirmation_code')
    user = get_object_or_404(User, username=request.data.get('username'))
    user_code = user.confirmation_code

    if request_code != user_code:
        return Response(
            'confirmation code not valid', status=status.HTTP_400_BAD_REQUEST
        )

    token = get_tokens_for_user(user)
    return Response(token)


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def get_or_patch_user(request):

    if request.method == 'GET':
        # Я так понимаю, что если есть запрос от юзера на /me
        # то этот юзер есть в базе, раз запрос проходит через
        # permissions.IsAuthenticated

        serializer = CreateUserSerializer(request.user)
        return Response(serializer.data)

    if request.method == 'PATCH':
        # См. выше

        serializer = CreateUserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    permission_classes = (permissions.IsAuthenticated, IsAdmin,)
    serializer_class = CreateUserSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
