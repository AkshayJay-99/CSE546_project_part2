from django.apps import AppConfig
import pandas as pd


class ImglookupAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "imglookup_app"
    
    def ready(self):
        # Execute the management command to load data into the DataFrame
        global df
        result_path = 'cc_project/imglookup_app/static/classification_results.csv'
        df = pd.read_csv(result_path)
