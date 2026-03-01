from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.LoginViewCustom.as_view(), name="login"),
    path("logout/", views.LogoutViewCustom.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
]