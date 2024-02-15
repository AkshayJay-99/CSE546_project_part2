from django.apps import AppConfig
import pandas as pd


class ImglookupAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "imglookup_app"
    
    def ready(self):
        # Execute the management command to load data into the DataFrame
        global df
        result_path = 'C:\Masters-Doc\ASU\courses\CSE546-Cloud-Computing\CC_project\cc_project\cc_project\static\classification_results.csv'
        df = pd.read_csv(result_path)
