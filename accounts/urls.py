from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # login choice + 3 role-specific login pages
    path('accounts/login/', views.login_choice, name='login'),
    path('accounts/login/family/', views.login_family, name='login_family'),
    path('accounts/login/hospital/', views.login_hospital, name='login_hospital'),
    path('accounts/login/police/', views.login_police, name='login_police'),

    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/register/', views.register_choice, name='register_choice'),
    path('accounts/register/family/', views.register_family, name='register_family'),
    path('accounts/register/hospital/', views.register_hospital, name='register_hospital'),
    path('accounts/register/police/', views.register_police, name='register_police'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
]