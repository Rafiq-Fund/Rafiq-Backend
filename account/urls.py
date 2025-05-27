from django.urls import path
from account import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("logout/", views.logout, name="logout"),
    path("profile/", views.UserProfileView.as_view(), name="user-profile"),
    path('activate/<str:token>/', views.ActivateAccountView.as_view(), name='activate-account'),
]
