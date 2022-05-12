from rest_framework.generics import CreateAPIView
from rest_framework import viewsets, permissions, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User
from .permissions import IsAdminOrSuperuser
from .serializers import SignUpSerializer, TokenSerializer, UserSerializer, UserForMeSerializer
from rest_framework_simplejwt.views import TokenViewBase


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
