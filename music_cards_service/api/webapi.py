import math
import time
import traceback

from PIL import Image

from imager.cardcreator import generate_card_front, generate_card_back, generate_message_card
from metadata.albumdetails import search_songlink_album

SUPPORTED_MUSIC_SERVICES = {"apple": search_songlink_album}

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
    get_album_details = SUPPORTED_MUSIC_SERVICES[music_service.lower()]
    front_page = Image.new('RGB', (widthpixel, heightpixel), (255, 255, 255))
    error_count = 0
    for counter in range(len(entities)):
        try:
            album_details = get_album_details(entities[counter])
            album_front_image = generate_card_front(album_details, cardwidth, cardheight)
        except Exception as e:
            error_message = "Unable to process entity [%s]\n" % entities[
                counter] + "Error Stack trace:\n%s" % traceback.format_exc()
            print(error_message)
            album_front_image = generate_message_card(error_message, cardwidth, cardheight)
            error_count = error_count + 1
        album_front_image = album_front_image.rotate(90, expand=True)
        x = (counter % 2) * cardheight
        y = math.floor(counter / 2) * cardwidth
        front_page.paste(album_front_image, (x + print_margin_left, y))
    front_page.save(output_path)
    if error_count > 0:
        return "_" + str(error_count) + "err"
    else:
        return ""


def get_back_page(cards_per_page, music_service, entities, output_path):
    if cards_per_page != 8:
        raise UnboundLocalError("Can only process 8 card template")
    if len(entities) > 8:
        raise UnboundLocalError("Can only process upto 8 cards")
    get_album_details = SUPPORTED_MUSIC_SERVICES[music_service.lower()]
    back_page = Image.new('RGB', (widthpixel, heightpixel), (255, 255, 255))
    error_count = 0

    for counter in range(len(entities)):
        try:
            album_details = get_album_details(entities[counter])
            album_back_image = generate_card_back(album_details, cardwidth, cardheight)
        except Exception as e:
            error_message = "Unable to process entity [%s]\n" % entities[
                counter] + "Error Stack trace:\n%s" % traceback.format_exc()
            print(error_message)
            album_back_image = generate_message_card(error_message, cardwidth, cardheight)
        album_back_image = album_back_image.rotate(270, expand=True)
        x = ((counter + 1) % 2) * cardheight
        y = math.floor(counter / 2) * cardwidth
        back_page.paste(album_back_image, (x, y))
    back_page.save(output_path)
    if error_count > 0:
        return "_" + str(error_count) + "err"
    else:
        return ""
