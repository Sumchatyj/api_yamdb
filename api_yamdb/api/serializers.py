from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field="slug", queryset=Genre.objects.all(), many=True
    )
    rating = serializers.SerializerMethodField(required=False)

    class Meta:
        fields = "__all__"
        model = Title

    def validate_category(self, value):
        if value is not None:
            category = Category.objects.get(slug=value)
            if category:
                return value
            else:
                raise serializers.ValidationError("Такой категории нет!")

    def validate_genre(self, values):
        if len(values) > 0:
            if not Genre.objects.filter(slug__in=values):
                raise serializers.ValidationError("Такого жанра нет!")
            else:
                return values

    def to_representation(self, instance):
        data = super(TitleSerializer, self).to_representation(instance)
        category_slug = data.pop("category")
        name_category = instance.category.name
        category = {"category": {"name": name_category, "slug": category_slug}}
        genre_data = data.pop("genre")
        genre_list = []
        genre_dict = {"genre": genre_list}
        for genre in genre_data:
            name = Genre.objects.get(slug=genre).name
            genre_dict_one = {"name": name, "slug": genre}
            genre_list.append(genre_dict_one)
        data.update(category)
        data.update(genre_dict)
        return data

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg("score"))["score__avg"]
        if rating is None:
            return rating
        return round(rating)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date")
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username", read_only=True
    )

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    class Meta:
        fields = ("username", "email")
        model = User


class TokenSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields["confirmation_code"] = serializers.CharField()
        self.fields.pop("password")

    def validate(self, attrs):
        user = get_object_or_404(User, username=attrs["username"])
        if user.confirmation_code == attrs["confirmation_code"]:
            refresh = self.get_token(user)
            data = {"access": str(refresh.access_token)}
            return data
        else:
            raise ValidationError("неверный confirmation_code")


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        model = User


class UserForMeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        read_only_fields = ("role",)
        model = User
