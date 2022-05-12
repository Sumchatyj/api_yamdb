from django.urls import path, include
from .views import SignUpView, TokenView, UserViewset, ReviewsViewSet, CommentsViewSet
from rest_framework.routers import DefaultRouter


router_v1 = DefaultRouter()
router_v1.register(r"users", UserViewset, "Users")

router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet,
    basename='review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comment'
)

urlpatterns = [
    path('v1/auth/signup/', SignUpView.as_view()),
    path('v1/auth/token/', TokenView.as_view()),
    path("v1/", include(router_v1.urls)),
]
