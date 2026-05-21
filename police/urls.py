from django.urls import path
from . import views

app_name = 'police'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cases/', views.regional_cases, name='regional_cases'),
    path('cases/<int:pk>/', views.case_detail, name='case_detail'),
    path('matches/', views.nearby_matches, name='nearby_matches'),
    path('hospitals/', views.search_hospitals, name='search_hospitals'),
    path('archived/', views.archived_cases, name='archived_cases'),
]
