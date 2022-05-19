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
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.SerializerMethodField(required=False)

    class Meta:
        fields = "__all__"
        model = Title

    def create(self, validated_data):
        slug_category = self.context["request"].data.get("category")
        validated_data["category"] = Category.objects.get(slug=slug_category)
        slugs_genre = self.context["request"].data.getlist("genre")
        genres = []
        for slug in slugs_genre:
            genre = Genre.objects.filter(slug=slug)
            genres.append(genre[0])
        validated_data["genre"] = genres
        genres = validated_data.pop("genre")
        title = Title.objects.create(**validated_data)
        title.genre.set(genres)
        return title

    def update(self, instance, validated_data):
        slug_category = self.context["request"].data.get("category")
        validated_data["category"] = Category.objects.get(slug=slug_category)
        instance.category = validated_data.get('category', instance.category)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

    def validate_category(self, value):
        try:
            value = Category.objects.get(slug=value)
        except Exception:
            raise serializers.ValidationError("Такой категории нет!")
        return value

    def validate_genre(self, values):
        values_genre = []
        for value in values:
            try:
                value_genre = Genre.objects.filter(slug=value)
                values_genre.append(value_genre[0])
            except Exception:
                raise serializers.ValidationError("Такого жанра нет!")
        return values_genre

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score'))['score__avg']
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
