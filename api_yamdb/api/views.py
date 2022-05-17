from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filter
from rest_framework import (filters, mixins, permissions, serializers, status,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from reviews.models import Category, Genre, Review, Title
from users.models import User

from .filters import FilterTitle
from .pagination import (CategoriesPagination, GenresPagination,
                         TitlesPagination)
from .permissions import (IsAdminOrSuperuser, IsAdminOrSuperuserOrReadOnly,
                          IsAuthorOrStaffOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleSerializer, TokenSerializer,
                          UserForMeSerializer, UserSerializer)


class CrLstDstViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CategoryViewSet(CrLstDstViewSet):
    queryset = Category.objects.order_by("id")
    serializer_class = CategorySerializer
    lookup_field = "slug"
    permission_classes = [
        IsAdminOrSuperuserOrReadOnly,
    ]
    filter_backends = (filters.SearchFilter,)
    pagination_class = CategoriesPagination
    search_fields = ("name",)


class GenreViewSet(CrLstDstViewSet):
    queryset = Genre.objects.order_by("id")
    serializer_class = GenreSerializer
    lookup_field = "slug"
    permission_classes = [
        IsAdminOrSuperuserOrReadOnly,
    ]
    filter_backends = (filters.SearchFilter,)
    pagination_class = GenresPagination
    search_fields = ("name",)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.order_by("id")
    serializer_class = TitleSerializer
    permission_classes = [
        IsAdminOrSuperuserOrReadOnly,
    ]
    filter_backends = (filter.DjangoFilterBackend,)
    pagination_class = TitlesPagination
    filterset_class = FilterTitle


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrStaffOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.order_by("-pub_date")

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        if title.reviews.filter(author=self.request.user).exists():
            raise serializers.ValidationError(
                "Можно оставить только один отзыв!"
            )
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrStaffOrReadOnly,)

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, pk=review_id)
        return review.comments.order_by("-pub_date")

    def perform_create(self, serializer):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)


class SignUpView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )


class TokenView(TokenViewBase):
    permission_classes = (permissions.AllowAny,)
    serializer_class = TokenSerializer


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrSuperuser,)
    lookup_field = "username"
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)

    @action(
        detail=False,
        methods=["get", "patch"],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        user = self.request.user
        if request.method == "GET":
            serializer = UserForMeSerializer(user)
            return Response(serializer.data)
        if request.method == "PATCH":
            serializer = UserForMeSerializer(
                user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            raise serializers.ValidationError("Ошибка валидации")
