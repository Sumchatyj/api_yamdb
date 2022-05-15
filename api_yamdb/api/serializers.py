from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from reviews.models import Comment, Review, Title
from users.models import User


def user_validation(data):
    if data.get("username") == 'me':
        raise ValidationError('Недопустимый юзернейм')
    return data


class TitleSerializer(serializers.ModelSerializer):
    raiting = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name', 'year', 'category', 'raiting')
        model = Title

    def get_raiting(self, obj):
        reviews = obj.reviews.all()
        count = reviews.count()
        score_sum = 0
        for i in reviews:
            score_sum += i.score
        raiting = round(score_sum / count)
        return raiting


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = ('username', 'email')
        model = User

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.confirmation_code = default_token_generator.make_token(user)
        user.email_user(
            'Welcome!',
            f'Your confirmation code: {user.confirmation_code}',
        )
        user.save()
        return user

    def validate(self, data):
        return user_validation(data)


class TokenSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields["confirmation_code"] = serializers.CharField()
        self.fields.pop("password")

    def validate(self, attrs):
        user = get_object_or_404(User, username=attrs['username'])
        if user.confirmation_code == attrs['confirmation_code']:
            refresh = self.get_token(user)
            data = {
                "access": str(refresh.access_token)
            }
            return data
        else:
            raise ValidationError('неверный confirmation_code')


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User

    def validate(self, data):
        return user_validation(data)


class UserForMeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)
        model = User

    def validate(self, data):
        return user_validation(data)
