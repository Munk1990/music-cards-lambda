import json
import os
import random
import string

from api.webapi import get_front_page, get_back_page, copy_to_s3

S3_CACHE_BUCKET = os.environ['CACHE_BUCKET']
IMAGE_DIRECTORY = "files/"
TMP_FILE_LOCATION = "/tmp/full_page.jpg"
S3_LINK_TEMPLATE = "https://music-cards-cache.s3.amazonaws.com/"
ERROR_TAG = "error"
FRONT_TAG = "front"
BACK_TAG = "back"
IMAGE_EXTENSION = ".jpg"


def get_front(event, context):
    albumlist = event["queryStringParameters"]["albums"].split(",")
    if 'youtubeKey' in event["queryStringParameters"]:
        youtube_key = event["queryStringParameters"]["youtubeKey"]
    else:
        youtube_key = None
    print ("youtubekey [%s]" % youtube_key)
    print("Printing front page for albums: %s" % albumlist)

    file_id = IMAGE_DIRECTORY + FRONT_TAG + "_" + lower_random_string(5)
    s3_path = file_id + IMAGE_EXTENSION

    get_front_page(8, albumlist, TMP_FILE_LOCATION, youtube_key)
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
    albumlist = event["queryStringParameters"]["albums"].split(",")
    print("request:[%s]" % event)
    if 'youtubeKey' in event["queryStringParameters"]:
        youtube_key = event["queryStringParameters"]["youtubeKey"]
    else:
        youtube_key = None
    print ("youtubekey [%s]" % youtube_key)
    print("Printing back page for albums: %s" % albumlist)

    file_id = IMAGE_DIRECTORY + BACK_TAG + "_" + lower_random_string(5)
    s3_path = file_id + IMAGE_EXTENSION

    get_back_page(8, albumlist, TMP_FILE_LOCATION, youtube_key)
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


def lower_random_string(length):  # define the function and pass the length as argument
    # Print the string in Lowercase
    result = ''.join(
        (random.choice(string.ascii_lowercase) for x in range(length)))  # run loop until the define length
    return result