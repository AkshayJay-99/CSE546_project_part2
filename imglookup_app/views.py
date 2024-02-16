from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from imglookup_app.apps import df


# Create your views here.

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



