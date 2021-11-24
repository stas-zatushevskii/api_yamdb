from django.db.models import Avg
from rest_framework import serializers
from rest_framework.validators import UniqueForYearValidator, UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title, User
from django.db.models import EmailField, CharField
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError


class CreateUserSerializer(serializers.ModelSerializer):
    email = EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name
        )
        instance.last_name = validated_data.get(
            'last_name', instance.last_name
        )
        instance.bio = validated_data.get('bio', instance.bio)
        instance.save()
        return instance

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User


class CreateUserInBaseSerializer(serializers.ModelSerializer):

    email = EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = ('username', 'email')
        model = User
        read_only_fields = ('confirmation_code',)


class CreateTokenSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'confirmation_code')
        model = User
        read_only_fields = ('username', )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ('id',)
        validators = UniqueForYearValidator(queryset=Title.objects.all(),
                                            field='pk',
                                            date_field='published',
                                            message='Неверно указан год')

    def get_rating(self, obj):
        try:
            rating = obj.reviews.aggregate(Avg('score'))
            return rating.get('score__avg')
        except TypeError:
            return None


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ('id', 'title', 'author', 'pub_date')

    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        request = self.context['request']
        if request.method == 'POST':
            if Review.objects.filter(author=request.user,
                                     title=title).exists():
                raise ValidationError(
                    'Можно оставлять только одно ревью к тайтлу'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('id', 'author', 'pub_date', 'reviews', 'title')
