from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from imglookup_app.apps import df
import threading


# Create your views here.
'''
@csrf_exempt
def imglookup(request):
    if request.method == 'POST' and 'inputFile' in request.FILES:
        input_file = request.FILES['inputFile']
        input_file_withoutextension = input_file.name.split('.')[0]
        filtered_df = df[df['Image']==input_file_withoutextension]
        return_value = filtered_df.iloc[0]['Results']
        return HttpResponse(f"{input_file.name.split('.')[0]}:{return_value}")
    else:
        return HttpResponse("Invalid request")
'''
@csrf_exempt
def imglookup(request):
    if request.method == 'POST' and 'inputFile' in request.FILES:
        input_file = request.FILES['inputFile']
        input_file_withoutextension = input_file.name.split('.')[0]

        # Define a function to process the request
        def process_request():
            filtered_df = df[df['Image'] == input_file_withoutextension]
            return_value = filtered_df.iloc[0]['Results']
            response_text = f"{input_file.name.split('.')[0]}:{return_value}"
            return HttpResponse(response_text)

        # Create and start a new thread to process the request
        thread = threading.Thread(target=process_request)
        thread.start()
    else:
        return HttpResponse("Invalid request")
