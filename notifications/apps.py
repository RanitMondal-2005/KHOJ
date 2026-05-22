from django.apps import AppConfig
class NotificationsConfig(AppConfig): # Configuration for the notifications app just like we did for the matching app signals
    default_auto_field = 'django.db.models.BigAutoField' # Auto-incrementing primary key meaning each notification will have a unique ID
    name = 'notifications' # Name of the app
