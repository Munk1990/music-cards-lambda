import json

import json
import os

import boto3

# import requests
import botocore

from api.webapi import get_front_page, get_back_page

S3_CACHE_BUCKET = os.environ['CACHE_BUCKET']
IMAGE_DIRECTORY = "files/"
TMP_FILE_LOCATION = "/tmp/full_page.jpg"
S3_LINK_TEMPLATE = "https://music-cards-cache.s3.amazonaws.com/"


def lambda_handler(event, context):

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }


def get_front(event, context):
    print("Printing front page")
    get_front_page(8, "apple", [155658405, 1499378108, 1440870373], "/tmp/front_page.jpg")
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "get front code",
            # "location": ip.text.replace("\n", "")
        }),
    }


def get_back(event, context):
    print(event)
    albumlist = event["queryStringParameters"]["albums"].split(",")
    print("Printing back page for albums: %s" % albumlist)

    file_name = IMAGE_DIRECTORY + "_".join("{0}".format(n) for n in albumlist) + "_back.jpg"
    s3_url = S3_LINK_TEMPLATE + file_name
    if cache_exists(file_name):
        print("File exists")

    else:
        print("File does not exist")
        get_back_page(8, "apple", albumlist, TMP_FILE_LOCATION)
        copy_to_s3(TMP_FILE_LOCATION, S3_CACHE_BUCKET, file_name)
    return {
        "statusCode": 302,
        "headers" : {'Location' : s3_url},
        "body": json.dumps({
            "message": s3_url,
        }),
    }


def cache_exists(path):
    s3 = boto3.resource('s3')
    try:
        s3.Object(S3_CACHE_BUCKET, path).load()
        return True
    except:
        return False


def copy_to_s3(temp_file_location, s3_bucket, s3_path):
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(temp_file_location, s3_bucket, s3_path)



def retrieve_image(s3_bucket, s3_path):
    s3 = boto3.resource('s3')
    s3.meta.client
