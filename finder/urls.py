from django.urls import path
from finder import views

app_name = "finder"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("sign-up/", views.signUp, name="sign-up"),
    path("login/", views.login, name="login"),
]