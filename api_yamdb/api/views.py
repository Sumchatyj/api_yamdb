from rest_framework.generics import CreateAPIView
from rest_framework import viewsets, permissions, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User
from .permissions import IsAdminOrSuperuser
from .serializers import SignUpSerializer, TokenSerializer, UserSerializer, UserForMeSerializer, CommentSerializer, ReviewSerializer
from rest_framework_simplejwt.views import TokenViewBase
from django.shortcuts import get_object_or_404

from reviews.models import Review, Title


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review)
        serializer.save(author=self.request.user, review=review)


class SignUpView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = SignUpSerializer


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

    @action(detail=False, methods=['get', 'patch'], permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        user = self.request.user
        if request.method == "GET":
            serializer = UserForMeSerializer(user)
            return Response(serializer.data)
        if request.method == "PATCH":
            serializer = UserForMeSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            raise serializers.ValidationError("Ошибка валидации")
