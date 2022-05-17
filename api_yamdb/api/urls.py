from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentsViewSet, GenreViewSet,
                    ReviewsViewSet, SignUpViewSet, TitleViewSet, TokenView,
                    UserViewset)

router_v1 = DefaultRouter()
router_v1.register(r"auth/signup", SignUpViewSet, "signup")
router_v1.register(r"users", UserViewset, "users")
router_v1.register(r"categories", CategoryViewSet, basename="categories")
router_v1.register(r"genres", GenreViewSet, basename="genres")
router_v1.register(r"titles", TitleViewSet, basename="titles")
router_v1.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewsViewSet, basename="review"
)
router_v1.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentsViewSet,
    basename="comment",
)

urlpatterns = [
    path("v1/auth/token/", TokenView.as_view()),
    path("v1/", include(router_v1.urls)),
]
