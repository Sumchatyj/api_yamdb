from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _


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
        try:
            Category.objects.get(slug=value)
        except Exception:
            raise serializers.ValidationError("Такой категории нет!")
        return value

    def validate_genre(self, values):
        for value in values:
            try:
                Genre.objects.filter(slug=value)
            except Exception:
                raise serializers.ValidationError("Такого жанра нет!")
        return values

    def create(self, validated_data):
        category = validated_data.pop("category")
        genres = validated_data.pop("genre")
        title = Title.objects.create(**validated_data)
        title.category = category
        title.genre.set(genres)
        title.save()
        return title

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


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    def validate(self, attrs):
        if attrs.get('username') == 'me':
            raise ValidationError("неверный username!")
        return attrs


class TokenSerializer(serializers.Serializer):
    username_field = User.USERNAME_FIELD
    token_class = None

    default_error_messages = {
        "no_active_account": _("No active account found with the given credentials")
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields["confirmation_code"] = serializers.CharField()
        
    def validate(self, attrs):
        user = get_object_or_404(User, username=attrs["username"])
        if user.confirmation_code == attrs["confirmation_code"]:
            refresh = RefreshToken.for_user(user)
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


class UserForMeSerializer(UserSerializer):

    class Meta:
        fields = ('__all__')
        read_only_fields = ("role",)
        model = User
