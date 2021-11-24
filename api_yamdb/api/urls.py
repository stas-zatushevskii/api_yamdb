from django.urls import include, path
from rest_framework.routers import DefaultRouter
from reviews.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                           ReviewViewSet, TitleViewSet)

from .views import UsersViewSet, create_token, create_user, get_or_patch_user

router = DefaultRouter()

router.register('users', UsersViewSet)
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='ReViewSet'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='CommentViewSet'
)

urlpatterns = [
    path('v1/users/me/', get_or_patch_user),
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', create_user),
    path('v1/auth/token/', create_token),
]
