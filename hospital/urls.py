from django.urls import path
from . import views

app_name = 'hospital'
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('patients/add/', views.add_patient, name='add_patient'),
    path('patients/', views.view_patients, name='view_patients'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/identify/', views.mark_identified, name='mark_identified'),
    path('matches/', views.match_alerts, name='match_alerts'),
    path('matches/<int:pk>/reject/', views.reject_match, name='reject_match'),
    path('resolved/', views.resolved_patients, name='resolved_patients'),
]
