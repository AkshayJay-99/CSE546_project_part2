from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from imglookup_app.apps import df
import boto3
import os
import time
import concurrent.futures
import requests

s3_in_bucket = '1229059769-in-bucket'
s3_out_bucket = '1229059769-out-bucket'
s3 = boto3.client('s3')

sqs_req_queue = '1229059769-req-queue'
sqs_req_url = 'https://sqs.us-east-1.amazonaws.com/533267431319/1229059769-req-queue'
sqs = boto3.client('sqs', region_name='us-east-1')

ec2_instance_ids = ['i-076ff9cd3fa9d5c78', 'i-072e2192ebef2c6c4', 'i-09c3e439d0091156a', 'i-0dbb687d7ddabcbd3', 'i-0a6d49fbd52d8aefa', 'i-0b313197f356d0f2a', 'i-07975344fb98c50f2', 'i-027b01d4637907976', 'i-0669ce2be7099542f', 'i-041898d207a9b6a7e', 'i-001d1a0fbf0db9611', 'i-01b28d1e1b5fc249d', 'i-01f01b6941f8ce643', 'i-0114d1c66d351d304', 'i-02493c472fd4c2b95', 'i-0e89e10f9d19d2562', 'i-0daf89b037b464d8f', 'i-0ba531c5cd85cec75']
lb_ec2_instance = ['i-07ea64f7f0d415e94']
lb_ec2_url = 'http://3.93.2.0:8000/'
#lb_ec2_url = 'http://127.0.0.1:9000/'
ec2 = boto3.client('ec2')


flag = 0
count = 1
max_ec2_count = 20
result_count = 0

image_folder = 'imglookup_app/static/images'

# Create your views here.

@csrf_exempt
def imglookup(request):
    if request.method == 'POST' and 'inputFile' in request.FILES:
        global count
        global flag
        input_file = request.FILES['inputFile']
        file_name = input_file.name
        
        local_file_path = image_folder+'/'+file_name
        
        # Save the file to the local folder
        with open(local_file_path, 'wb') as local_file:
            local_file.write(input_file.read())
            
        upload_folder_to_s3(local_file_path, s3_in_bucket, file_name)
        
        send_messages_to_sqs(file_name)
        
        if count == 1:
            response = ec2.start_instances(InstanceIds=ec2_instance_ids[:8])
        if count > 10:
            #start_app_tier_instances(count)
            response = ec2.start_instances(InstanceIds=ec2_instance_ids[10:])
            
        #running_instance_ids = get_running_instance_ids(ec2_instance_ids)
        # sqs_message_count = check_sqs_message_count()
        # if sqs_message_count == 0:
        #     response = ec2.stop_instances(InstanceIds=ec2_instance_ids)
        count+=1
        # send image requests
        # send_image_request(lb_ec2_url, input_file)
        #response = requests.post(lb_ec2_url, files={'imageFile':input_file})
        with open(local_file_path, 'rb') as img_file:
            # Define the data to be sent in the POST request
            data = {'imageFile': img_file}
            # Send the POST request
            response = requests.post(lb_ec2_url, files=data)
        
        del_messages_from_sqs()
        
        response_sqs = sqs.get_queue_attributes(
            QueueUrl=sqs_req_url,
            AttributeNames=['ApproximateNumberOfMessages']
        )
        
        approximate_message_count = int(response_sqs['Attributes']['ApproximateNumberOfMessages'])
        
        
        if approximate_message_count==0 or count==9 or count==50:
            response = ec2.stop_instances(InstanceIds=ec2_instance_ids)
                

        # Print error message if failed
        if response.status_code != 200:
            return HttpResponse(response.url)
        else:
            return HttpResponse(response.text)
      
    else:
        return HttpResponse("Invalid request")
    
count = 1

def upload_folder_to_s3(local_path, s3_bucket, s3_key):
    
    #uploading images to the s3 bucket
    s3.upload_file(local_path, s3_bucket, s3_key)
    
def send_messages_to_sqs(file_name):
    
    message_body = f"'{file_name}' uploaded!"
    sqs.send_message(QueueUrl=sqs_req_url, MessageBody=message_body)
    
def del_messages_from_sqs():
    response = sqs.receive_message(QueueUrl=sqs_req_url, MaxNumberOfMessages=1)
    messages = response.get('Messages', [])

    if messages:
        msg = messages[0]
        receipt_handle = msg['ReceiptHandle']
        sqs.delete_message(QueueUrl=sqs_req_url, ReceiptHandle=receipt_handle)

    
        
def stop_app_tier_instances():
    response = ec2.stop_instances(InstanceIds=ec2_instance_ids)

               
# def check_ec2_instance_status(instance_ids, timeout=60):
#     """
#     Check the status of EC2 instances based on their instance IDs.

#     :param instance_ids: List of EC2 instance IDs
#     :param timeout: Timeout in seconds (default is 90 seconds)
#     :return: Dictionary mapping instance ID to its status (e.g., {'i-12345678': 'running', ...})
#     """
#     start_time = time.time()

#     while True:
#         response = ec2.describe_instances(InstanceIds=instance_ids)

#         instance_status = {}
#         for reservation in response['Reservations']:
#             for instance in reservation['Instances']:
#                 instance_id = instance['InstanceId']
#                 state = instance['State']['Name']
#                 instance_status[instance_id] = state

#         # Check if all instances are in 'running' state
#         all_running = all(status == 'running' for status in instance_status.values())
#         if all_running:
#             return True

#         # Check if timeout has been reached
#         elapsed_time = time.time() - start_time
#         if elapsed_time >= timeout:
#             return False
        
#         # Wait for a few seconds before checking again
#         time.sleep(5)
        
#def send_image_request(url, image_file):
    # try:
    #     with open(image_path, 'rb') as image_file:
    #         response = requests.post(url, files={'image': image_file})
            
    # except requests.RequestException as e:
    #     print(f"Request to {url} failed: {e}")
    
    # image_file = {"imageFile": open(image_path,'rb')}
    # response = requests.post(url, files={'imageFile':image_file}, headers = {'Content-Type': 'multipart/form-data'})

    # # Print error message if failed
    # if response.status_code != 200:
    #     return HttpResponse(response.url)
    # else:
    #     return HttpResponse(response.text)
        
def check_sqs_message_count():
    response = sqs.get_queue_attributes(
    QueueUrl=sqs_req_url,
    AttributeNames=['ApproximateNumberOfMessages']
    )

    approximate_message_count = int(response['Attributes']['ApproximateNumberOfMessages'])
    return approximate_message_count
        
    
# def get_running_instance_ids(instance_ids, timeout=90):
#     """
#     Get the instance IDs of EC2 instances that are in the 'running' state.

#     :param instance_ids: List of EC2 instance IDs
#     :param timeout: Timeout in seconds (default is 90 seconds)
#     :return: List of instance IDs in 'running' state
#     """
#     start_time = time.time()
#     running_instance_ids = []

#     while True:
#         response = ec2.describe_instances(InstanceIds=instance_ids)

#         for reservation in response['Reservations']:
#             for instance in reservation['Instances']:
#                 instance_id = instance['InstanceId']
#                 state = instance['State']['Name']
#                 if state == 'running':
#                     running_instance_ids.append(instance_id)

#         # Check if all instances are in 'running' state
#         if len(running_instance_ids) >=1:
#             return running_instance_ids

#         # Check if timeout has been reached
#         elapsed_time = time.time() - start_time

#         if elapsed_time >= timeout:
#             return running_instance_ids

#         # Wait for a few seconds before checking again
#         time.sleep(5)

# def start_app_tier_instances(count):
#     if count>10:
#         response = ec2.start_instances(InstanceIds=ec2_instance_ids[10:])
#         flag = 1
#     elif count==10:
#         response = ec2.start_instances(InstanceIds=ec2_instance_ids[:10])
#         flag = 0.5
   



