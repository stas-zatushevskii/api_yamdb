from api.filters import TitleFilter
from api.permissions import IsAdminOrReadOnly, UserPermission
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleCreateSerializer, TitleSerializer)
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.pagination import PageNumberPagination

from .models import Category, Genre, Review, Title


class CustomMixin(ListModelMixin, CreateModelMixin,
                  DestroyModelMixin, viewsets.GenericViewSet):
    pass


class CategoryViewSet(CustomMixin):
    """API для категорий."""
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CustomMixin):
    """API для жанров."""
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """API для произведений."""
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    ordering_fields = ('name',)
    ordering = ('name',)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (UserPermission,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        new_queryset = title.reviews.all()
        return new_queryset

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)
        serializer.is_valid(raise_exception=True)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (UserPermission,)

    def get_queryset(self):
        review = get_object_or_404(Review,
                                   title_id=self.kwargs.get('title_id'),
                                   id=self.kwargs.get('review_id'))
        new_queryset = review.comments.all()
        return new_queryset

    def perform_create(self, serializer):
        review = get_object_or_404(Review,
                                   title_id=self.kwargs.get('title_id'),
                                   id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, reviews=review)
