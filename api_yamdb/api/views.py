from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, serializers, viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from reviews.models import Category, Genre, Review, Title
from .pagination import CategoriesPagination, GenresPagination
from .permissions import (IsAdminOrSuperuser, IsAuthorOrStaffOrReadOnly,
                          IsAdminOrSuperuserOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          SignUpSerializer, TitleSerializer,
                          TitleCreateSerializer, TokenSerializer,
                          UserForMeSerializer, UserSerializer)
from users.models import User


class CrLstDstViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    pass


class CrLstUpdDstViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                         mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    pass


class MultiSerializerViewSetMixin(object):
    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(MultiSerializerViewSetMixin, self).get_serializer_class()


class CategoryViewSet(CrLstDstViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrSuperuserOrReadOnly, ]
    filter_backends = (filters.SearchFilter,)
    pagination_class = CategoriesPagination
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CrLstDstViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrSuperuserOrReadOnly, ]
    filter_backends = (filters.SearchFilter,)
    pagination_class = GenresPagination
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(MultiSerializerViewSetMixin, CrLstUpdDstViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrSuperuserOrReadOnly, ]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    pagination_class = GenresPagination
    filterset_fields = ('category', 'genre', 'name', 'year')
    serializer_action_classes = {
        'list': TitleSerializer,
        'create': TitleCreateSerializer,
        'retrieve': TitleSerializer,
        'partial_update': TitleCreateSerializer,
        'destroy': TitleSerializer,
    }
    lookup_field = 'slug'


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrStaffOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.order_by('-pub_date')

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        if title.reviews.filter(author=self.request.user).exists():
            raise serializers.ValidationError(
                'Можно оставить только один отзыв!')
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrStaffOrReadOnly,)

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, pk=review_id)
        return review.comments.order_by('-pub_date')

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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrSuperuser,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        user = self.request.user
        if request.method == "GET":
            serializer = UserForMeSerializer(user)
            return Response(serializer.data)
        if request.method == "PATCH":
            serializer = UserForMeSerializer(
                user, data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            raise serializers.ValidationError("Ошибка валидации")
