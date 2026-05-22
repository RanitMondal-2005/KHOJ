from django.apps import AppConfig
# compulsory format to use a signal in django & also register ur signals in settings.py via INSTALLED_APPS
class MatchingConfig(AppConfig): 
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'matching'

    def ready(self):
        import matching.signals  # means signals are imported and ready to use
