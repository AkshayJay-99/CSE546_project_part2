from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from imglookup_app.apps import df
import boto3
import os


# Create your views here.

@csrf_exempt
def imglookup(request):
    if request.method == 'POST' and 'inputFile' in request.FILES:
        input_file = request.FILES['inputFile']
        file_name = input_file.name
        local_folder_path = 'imglookup_app/static/images'
        local_file_path = os.path.join(local_folder_path,file_name)
        
        # Save the file to the local folder
        with open(local_file_path, 'wb') as local_file:
            local_file.write(input_file.read())
            
        s3_bucket = '1229059769-in-bucket'
        
        upload_folder_to_s3(local_file_path, s3_bucket, file_name)
            
        
    else:
        return HttpResponse("Invalid request")

def upload_folder_to_s3(local_path, s3_bucket, s3_key):
    s3 = boto3.client('s3')
    #uploading images to the s3 bucket
    s3.upload_file(local_path, s3_bucket, s3_key)




