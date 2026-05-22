from django.urls import path
from . import views

app_name = 'matching' # as we used namespace for the app

urlpatterns = [
    path('<int:pk>/', views.match_detail, name='match_detail'), # URL pattern for match detail view, expects an integer primary key (pk) to identify the specific match result to display
]
