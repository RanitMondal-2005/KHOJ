from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    # About Us page
    path('about/', views.about, name='about'),
    # login choice + 3 role-specific login pages
    path('accounts/login/', views.login_choice, name='login'),
    path('accounts/login/family/', views.login_family, name='login_family'),
    path('accounts/login/hospital/', views.login_hospital, name='login_hospital'),
    path('accounts/login/police/', views.login_police, name='login_police'),
    # Logout
    path('accounts/logout/', views.logout_view, name='logout'),
    # register choice + 3 role-specific registration pages
    path('accounts/register/', views.register_choice, name='register_choice'),
    path('accounts/register/family/', views.register_family, name='register_family'),
    path('accounts/register/hospital/', views.register_hospital, name='register_hospital'),
    path('accounts/register/police/', views.register_police, name='register_police'),
    # dashboard redirect according to user role
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
]