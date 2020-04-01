from django.urls import path
from finder import views

app_name = "finder"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("sign-up/", views.signUp, name="sign-up"),
    path("user_login/", views.user_login, name="user_login"),
    path("user_logout/", views.user_logout, name="user_logout"),
    path("support/", views.support, name="support"),
	path("settings/", views.settings, name="settings"),
	path("account/", views.account, name="account"),
	path("myBusinesses/", views.myBusinesses, name="myBusinesses"),
    path("adminPanel/", views.adminPanel, name="adminPanel"),
    path("adminPanel/<slug:business_name_slug>/", views.adminPanel, name="adminPanel"),
    path("find_food/", views.find_food, name="find_food"),
    path('find_food/<slug:business_name_slug>/', views.show_business, name='show_business'),
    path("reserve/", views.reserve, name="reserve"),
    path("addBusiness/", views.add_business, name="addBusiness"),
    path("curentReservation/", views.currentReservation, name="curentReservation"),
    path("cancelOffer/", views.cancelOffer, name="cancelOffer")
]