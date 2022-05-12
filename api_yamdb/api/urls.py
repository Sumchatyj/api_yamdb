from django.urls import path, include
from .views import SignUpView, TokenView, UserViewset
from rest_framework.routers import DefaultRouter


v1_router = DefaultRouter()
v1_router.register(r"users", UserViewset, "Users")

urlpatterns = [
    path('v1/auth/signup/', SignUpView.as_view()),
    path('v1/auth/token/', TokenView.as_view()),
    path("v1/", include(v1_router.urls)),
]
