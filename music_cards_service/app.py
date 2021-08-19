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
ERROR_TAG = "error"
FRONT_TAG = "front"
BACK_TAG = "back"
IMAGE_EXTENSION = ".jpg"


def get_front(event, context):
    print(event)
    albumlist = event["queryStringParameters"]["albums"].split(",")
    print("Printing front page for albums: %s" % albumlist)

    file_id = IMAGE_DIRECTORY + FRONT_TAG + "_" + ("_".join("{0}".format(n) for n in albumlist))
    s3_path = file_id + IMAGE_EXTENSION
    if cache_exists(s3_path):
        print("File %s exists" % (file_id + IMAGE_EXTENSION))
    else:
        print("File %s does not exist" % (file_id + IMAGE_EXTENSION))
        append_message = get_front_page(8, "apple", albumlist, TMP_FILE_LOCATION)
        s3_path = file_id + append_message + IMAGE_EXTENSION
        print("Copying to %s" % s3_path)
        copy_to_s3(TMP_FILE_LOCATION, S3_CACHE_BUCKET, s3_path)
    s3_url = S3_LINK_TEMPLATE + s3_path
    return {
        "statusCode": 302,
        "headers": {'Location': s3_url},
        "body": json.dumps({
            "message": s3_url,
        }),
    }


def get_back(event, context):
    print(event)
    albumlist = event["queryStringParameters"]["albums"].split(",")
    print("Printing back page for albums: %s" % albumlist)

    file_id = IMAGE_DIRECTORY + BACK_TAG + "_" + ("_".join("{0}".format(n) for n in albumlist))
    s3_path = file_id + IMAGE_EXTENSION
    if cache_exists(file_id):
        print("File %s exists" % (file_id + IMAGE_EXTENSION))
    else:
        print("File %s does not exist" % (file_id + IMAGE_EXTENSION))
        append_message = get_back_page(8, "apple", albumlist, TMP_FILE_LOCATION)
        s3_path = file_id + append_message + IMAGE_EXTENSION
        print("Copying to %s" % s3_path)
        copy_to_s3(TMP_FILE_LOCATION, S3_CACHE_BUCKET, s3_path)
    s3_url = S3_LINK_TEMPLATE + s3_path
    return {
        "statusCode": 302,
        "headers": {'Location': s3_url},
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
