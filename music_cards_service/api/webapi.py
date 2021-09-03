import io
import math
import os
import time
import traceback

import boto3
from PIL import Image

from metadata.albumdetails import populate_album
from imager.cardcreator import generate_card_front, generate_card_back, generate_message_card

CARD_GENERATION = {"front": generate_card_front, "back" : generate_card_back}
try:
    S3_CACHE_BUCKET = os.environ['CACHE_BUCKET']
except KeyError:
    S3_CACHE_BUCKET = "NullBucket"
    print("Unable to fetch S3_CACHE_BUCKET from Environment. Setting it to [%s]" % S3_CACHE_BUCKET)
S3_CACHE_LOCATION = "cards/"

TMP_FILE_PATH = "/tmp/"
IMAGE_EXTN = ".jpg"

page_dimension = [203, 277]
dpi = 300
mmtoinch = 0.0393700787
print_margin_left = int(1.5 * 300 * mmtoinch)
print_margin_right = 0

widthpixel = int(page_dimension[0] * mmtoinch * dpi)
heightpixel = int(page_dimension[1] * mmtoinch * dpi)
cardwidth = int(heightpixel / 4)
cardheight = int((widthpixel - print_margin_left - print_margin_right) / 2)

curtime = time.strftime("%m%d%H%M")

print(
    "card dimensions are Width [%d] Height [%d]" % (int(cardwidth / dpi / mmtoinch), int(cardheight / dpi / mmtoinch)))


def get_front_page(cards_per_page, urls, output_path, youtube_key):
    if cards_per_page > 8:
        raise UnboundLocalError("Can only process up to 8 cards")
    front_page = Image.new('RGB', (widthpixel, heightpixel), (255, 255, 255))
    for counter in range(len(urls)):
        try:
            card = get_cache_or_generate_card(urls[counter], cardwidth, cardheight, "front", youtube_key)
        except Exception as e:
            error_message = "Unable to process entity [%s]\n" % urls[
                counter] + "Error Stack trace:\n%s" % traceback.format_exc()
            print(error_message)
            card = generate_message_card(error_message, cardwidth, cardheight)
        card = card.rotate(90, expand=True)
        x = (counter % 2) * cardheight
        y = math.floor(counter / 2) * cardwidth
        front_page.paste(card, (x + print_margin_left, y))
    front_page.save(output_path)


def get_back_page(cards_per_page, urls, output_path, youtube_key):
    if cards_per_page != 8:
        raise UnboundLocalError("Can only process 8 card template")
    if len(urls) > 8:
        raise UnboundLocalError("Can only process upto 8 cards")
    back_page = Image.new('RGB', (widthpixel, heightpixel), (255, 255, 255))
    for counter in range(len(urls)):
        try:
            card = get_cache_or_generate_card(urls[counter], cardwidth, cardheight, "back", youtube_key)
        except Exception as e:
            error_message = "Unable to process entity [%s]\n" % urls[
                counter] + "Error Stack trace:\n%s" % traceback.format_exc()
            print(error_message)
            card = generate_message_card(error_message, cardwidth, cardheight)
        card = card.rotate(270, expand=True)
        x = ((counter + 1) % 2) * cardheight
        y = math.floor(counter / 2) * cardwidth
        back_page.paste(card, (x, y))
    back_page.save(output_path)


def get_cache_or_generate_card(url, width, height, variant, youtube_key):
    album_details = populate_album(url, youtube_key)
    unique_album_id = album_details['entityUniqueId']
    file_id = "%s_%s_%s_%s.jpg" % (unique_album_id, width, height, variant)
    s3_location = S3_CACHE_LOCATION + file_id
    try:
        img = fetch_from_cache(S3_CACHE_BUCKET, s3_location)
        print("Cache hit [%s]" % s3_location)
        return img
    except:
        print("Cache miss [%s]" % s3_location)
        img = CARD_GENERATION[variant](album_details, width, height)
        img.save(TMP_FILE_PATH + variant + IMAGE_EXTN)
        copy_to_s3(TMP_FILE_PATH + variant + IMAGE_EXTN, S3_CACHE_BUCKET, s3_location)
        return img


def fetch_from_cache(bucket, key):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    obj = bucket.Object(key)
    response = obj.get()
    file_stream = response['Body']
    im = Image.open(file_stream)
    return im


def copy_to_s3(temp_file_location, s3_bucket, s3_path):
    s3 = boto3.resource('s3')
    print("Copying file from [%s] to bucket [%s] key [%s]" % (temp_file_location, s3_bucket, s3_path))
    s3.meta.client.upload_file(temp_file_location, s3_bucket, s3_path)


def _test_card_image(url, width, height, variant, youtube_key):
    album_details = populate_album(url, youtube_key)
    img = CARD_GENERATION[variant](album_details, width, height)
    img.show()


def get_card_for_url(url, youtube_key, local_save_location):
    album_details = populate_album(url, youtube_key)
    unique_album_id = "%s.%s" % (album_details["albumidtype"], album_details["albumid"])
    response = {"url": url, "id": unique_album_id}
    for variant in CARD_GENERATION:
        file_id = "%s_%s_%s_%s.jpg" % (unique_album_id, cardwidth, cardheight, variant)
        s3_location = S3_CACHE_LOCATION + file_id
        try:
            img = fetch_from_cache(S3_CACHE_BUCKET, s3_location)
            print("Cache hit [%s]" % s3_location)
        except:
            print("Cache miss [%s]" % s3_location)
            img = CARD_GENERATION[variant](album_details, cardwidth, cardheight)
            img.save(local_save_location + file_id)
            copy_to_s3(local_save_location + file_id, S3_CACHE_BUCKET, s3_location)
        response[variant] = s3_location
    return response

#result = get_card_for_url("https://music.youtube.com/playlist?list=OLAK5uy_nPR5guXk5lmX2Jf17V4GtknNEUm9K3RHI","AIzaSyD_reRtpI8lgBSJWFKKq3jpCYMM0WT_G_k","")