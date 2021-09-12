import json
import os
import random
import string
import traceback

from api.webapi import get_front_page, get_back_page, get_card_for_url, get_card_for_album

S3_CACHE_BUCKET = os.environ['CACHE_BUCKET']
IMAGE_DIRECTORY = "files/"
TMP_FILE_PATH = "/tmp/"
S3_LINK_TEMPLATE = "https://music-cards-cache.s3.amazonaws.com/"
ERROR_TAG = "error"
FRONT_TAG = "front"
BACK_TAG = "back"
IMAGE_EXTENSION = ".jpg"
PARAMETER_FILE = "resources/_do_not_checkin/params"


def get_front(event, context):
    albumlist = event["queryStringParameters"]["albums"].split(",")
    youtube_key = get_parameters_from_file(PARAMETER_FILE)["youtubeKey"]
    response = get_front_page(albumlist, youtube_key, TMP_FILE_PATH)
    s3_url = S3_LINK_TEMPLATE + response['front']
    return {
        "statusCode": 302,
        "headers": {'Location': s3_url},
        "body": json.dumps({
            "message": s3_url,
        }),
    }


def get_back(event, context):
    albumlist = event["queryStringParameters"]["albums"].split(",")
    youtube_key = get_parameters_from_file(PARAMETER_FILE)["youtubeKey"]
    response = get_back_page(albumlist, youtube_key, TMP_FILE_PATH)
    s3_url = S3_LINK_TEMPLATE + response['back']
    return {
        "statusCode": 302,
        "headers": {'Location': s3_url},
        "body": json.dumps({
            "message": s3_url,
        }),
    }


def get_card(event, context):
    print("get_card function called with request: [%s]" % event)
    albumurl = albumid = albumprovider = None
    if "albumUrl" in event["queryStringParameters"]:
        albumurl = event["queryStringParameters"]["albumUrl"]
    else:
        albumid = event["queryStringParameters"]["albumId"]
        albumprovider = event["queryStringParameters"]["provider"]
    print("request:[%s]" % event)
    youtube_key = get_parameters_from_file(PARAMETER_FILE)["youtubeKey"]
    response = {}
    try:
        if albumurl:
            response = get_card_for_url(albumurl, youtube_key, TMP_FILE_PATH)
        else:
            response = get_card_for_album(albumprovider, albumid, youtube_key, TMP_FILE_PATH)
        response["s3_url_back"] = S3_LINK_TEMPLATE + response['back']
        response["s3_url_front"] = S3_LINK_TEMPLATE + response['front']
        status_code = 200
    except Exception as e:
        status_code = 500
        response["exception"] = traceback.format_exc()
    return {
        "statusCode": status_code,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    }


def lower_random_string(length):  # define the function and pass the length as argument
    # Print the string in Lowercase
    result = ''.join(
        (random.choice(string.ascii_lowercase) for x in range(length)))  # run loop until the define length
    return result


def get_parameters_from_file(filepath):
    params = {}
    param_file = open(filepath, "r")
    lines = param_file.readlines()
    for line in lines:
        if len(line.strip()) > 0:
            params[line.split(":")[0]] = line.split(":")[1]
    return params
