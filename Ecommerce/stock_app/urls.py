from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth.views import LogoutView
from . import views
from .views import (
    ProductViewSet,
    register_api_view,
    login_api_view,
    logout_api_view,
    login_view,
    register_view,
    profile_view
)

# Create router instance
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

# API URLs - REST endpoints
api_urlpatterns = [
    path('', include(router.urls)),
    path('register/', register_api_view, name='api-register'),
    path('login/', login_api_view, name='api-login'),
    path('logout/', logout_api_view, name='api-logout'),
]

# Web URLs - Browser endpoints
urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', profile_view, name='profile'),
]