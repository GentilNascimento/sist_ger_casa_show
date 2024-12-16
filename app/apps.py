from django.apps import AppConfig
import os 

scheduler_initialized = False

class AppConfig(AppConfig):
    name = 'app'
    
    def ready(self):
        global scheduler_initialized
        if not scheduler_initialized and os.environ.get('RUN_MAIN') == 'true':
            from app.scheduler import start_scheduler
            start_scheduler()
            scheduler_initialized = True
