from django.urls import path
from . import views

app_name = 'family'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reports/', views.my_reports, name='my_reports'),
    path('reports/add/', views.add_report, name='add_report'),
    path('reports/<int:pk>/', views.report_detail, name='report_detail'),
    path('reports/<int:pk>/update/', views.add_case_update, name='add_case_update'),
    path('reports/<int:pk>/close/', views.close_case, name='close_case'),
    path('matches/', views.my_matches, name='my_matches'),
    path('matches/<int:pk>/reject/', views.reject_match, name='reject_match'),
    path('archived/', views.archived_cases, name='archived_cases'),
]
