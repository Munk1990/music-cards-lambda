import io
import math
import os
import time
import traceback

import boto3
from PIL import Image

from imager.cardcreator import generate_card_front, generate_card_back, generate_message_card
from metadata.albumdetails import search_songlink_album

SUPPORTED_MUSIC_SERVICES = {"apple": search_songlink_album}
CARD_GENERATION = {"back": generate_card_back, "front": generate_card_front}

S3_CACHE_BUCKET = os.environ['CACHE_BUCKET']
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


def get_front_page(cards_per_page, music_service, entities, output_path):
    if cards_per_page > 8:
        raise UnboundLocalError("Can only process up to 8 cards")
    front_page = Image.new('RGB', (widthpixel, heightpixel), (255, 255, 255))
    for counter in range(len(entities)):
        try:
            card = get_cache_or_generate_card(music_service, entities[counter], cardwidth, cardheight, "front")
        except Exception as e:
            error_message = "Unable to process entity [%s]\n" % entities[
                counter] + "Error Stack trace:\n%s" % traceback.format_exc()
            print(error_message)
            card = generate_message_card(error_message, cardwidth, cardheight)
        card = card.rotate(90, expand=True)
        x = (counter % 2) * cardheight
        y = math.floor(counter / 2) * cardwidth
        front_page.paste(card, (x + print_margin_left, y))
    front_page.save(output_path)


def get_back_page(cards_per_page, music_service, entities, output_path):
    if cards_per_page != 8:
        raise UnboundLocalError("Can only process 8 card template")
    if len(entities) > 8:
        raise UnboundLocalError("Can only process upto 8 cards")
    back_page = Image.new('RGB', (widthpixel, heightpixel), (255, 255, 255))
    for counter in range(len(entities)):
        try:
            card = get_cache_or_generate_card(music_service, entities[counter], cardwidth, cardheight, "back")
        except Exception as e:
            error_message = "Unable to process entity [%s]\n" % entities[
                counter] + "Error Stack trace:\n%s" % traceback.format_exc()
            print(error_message)
            card = generate_message_card(error_message, cardwidth, cardheight)
        card = card.rotate(270, expand=True)
        x = ((counter + 1) % 2) * cardheight
        y = math.floor(counter / 2) * cardwidth
        back_page.paste(card, (x, y))
    back_page.save(output_path)


def get_cache_or_generate_card(music_service, entity, width, height, variant):
    file_id = "%s_%s_%s_%s_%s.jpg" % (music_service, entity, width, height, variant)
    s3_location = S3_CACHE_LOCATION + file_id
    try:
        img = fetch_from_cache(S3_CACHE_BUCKET, s3_location)
        print("Cache hit [%s]" % s3_location)
        return img
    except:
        print("Cache miss [%s]" % s3_location)
        get_album_details = SUPPORTED_MUSIC_SERVICES[music_service.lower()]
        album_details = get_album_details(entity)
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


#get_front_page(8, "apple", ['880709749', '1103770960', '1569562341'], "testout2.jpg")