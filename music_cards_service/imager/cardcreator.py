import io
import textwrap
from urllib.request import urlopen

import requests
from PIL import Image, ImageDraw, ImageFont
from colorthief import ColorThief

from imager.helpertools import set_transparency, change_color_transparency, change_colors

font_bold = "resources/fonts/AnonymousPro/AnonymousPro-Bold.ttf"
font_italic = "resources/fonts/AnonymousPro/AnonymousPro-Italic.ttf"
font_regular = "resources/fonts/AnonymousPro/AnonymousPro-Regular.ttf"
font_ExtraCondensedExtraBold = 'resources/fonts/NotoSans/NotoSans-ExtraCondensedExtraBold.ttf'
font_ExtraCondensed = 'resources/fonts/NotoSans/NotoSans-ExtraCondensed.ttf'

RECORD_WATERMARK = "resources/img/record.png"


def _fetch_dominant_color(imageUrl):
    print("Fetching dominant color from URL:[%s]" % imageUrl)
    fd = urlopen(imageUrl)
    f = io.BytesIO(fd.read())
    color_thief = ColorThief(f)
    dominant = color_thief.get_color(quality=1)
    pallette = color_thief.get_palette(quality=1)

    if dominant[0] + dominant[1] + dominant[2] < 100 * 3:
        return dominant
    else:
        for color in pallette:
            if color[0] + color[1] + color[2] < 100 * 3:
                return color
    return int(dominant[0] / 3), int(dominant[1] / 3), int(dominant[2] / 3)


def _draw_border(im, borderpx, linewidthpx, linecolor):
    draw = ImageDraw.Draw(im)
    height = im.size[1]
    width = im.size[0]
    draw.rectangle((0 + borderpx, 0 + borderpx, width - borderpx, height - borderpx)
                   , outline=linecolor, width=linewidthpx)
    draw.rectangle((0, 0, width, height), outline=(255, 255, 255), width=borderpx)


def _draw_album_art(im, album_art_url, offsetpx, theme_color):
    fd = urlopen(album_art_url)
    f = io.BytesIO(fd.read())
    album_art = Image.open(f)
    draw = ImageDraw.Draw(im)
    width = im.size[0]
    draw.rectangle((offsetpx,offsetpx,width-offsetpx, width-offsetpx), fill=theme_color)
    art_width = album_art.size[0]
    art_height = album_art.size[1]
    if art_width >= art_height:
        art_resize_width =width - 2 * offsetpx
        art_resize_height =int((width - 2 * offsetpx)/art_width * art_height)
        album_art = album_art.resize((art_resize_width, art_resize_height))
        im.paste(album_art, (offsetpx, offsetpx + int((width - 2*offsetpx - art_resize_height)/2)))
    else:
        art_resize_height =width - 2 * offsetpx
        art_resize_width =int((width - 2 * offsetpx)/art_height * art_width)
        album_art = album_art.resize((art_resize_width, art_resize_height))
        im.paste(album_art, (offsetpx + int((width - 2*offsetpx - art_resize_width)/2), offsetpx))



def _print_album_and_artist(im, album, artist, font, font_size, offset):
    width = im.size[0]
    draw = ImageDraw.Draw(im)

    album_font = ImageFont.truetype(font_bold, 50)
    possible_chars = int((width - offset * 2) / album_font.getsize("a")[0])
    multiline_album = "\n".join(textwrap.wrap(album, possible_chars))
    draw.text((offset, width - offset / 2), multiline_album, fill=(0, 0, 0), font=album_font)

    artist_font = ImageFont.truetype(font_italic, 45)
    possible_chars = int((width - offset * 2) / artist_font.getsize("a")[0])
    multiline_artist = "\n".join(textwrap.wrap(artist, possible_chars))
    draw.text((offset, width + album_font.getsize_multiline(multiline_album)[1]),
              multiline_artist, fill=(0, 0, 0), font=artist_font)


def _print_qr_code(im, url, widthpx, offset, color):
    qrurl = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=" + url
    fd = urlopen(qrurl)
    f = io.BytesIO(fd.read())
    qr_code = Image.open(f)
    width = im.size[0]
    height = im.size[1]
    qr_code = qr_code.resize((widthpx, widthpx))
    qr_code_colored = change_color_transparency(change_colors(qr_code, (0, 0, 0), color), (255, 255, 255), 0)
    im.paste(qr_code_colored, (width - offset - widthpx, height - offset - widthpx), qr_code_colored)


def _print_release_info(im, year, genre, offset, color):
    height = im.size[1]
    draw = ImageDraw.Draw(im)
    release_font = ImageFont.truetype(font_bold, 40)
    release_info = "%s  /  %s" % (genre, year)
    draw.text((offset, height - offset - release_font.getsize(release_info)[1]), release_info,
              fill=color, font=release_font)


def _print_watermark(im, watermark_path, percent_position, transparency, center_color, offset):
    width = im.size[0]
    height = im.size[1]

    watermark = Image.open(watermark_path)
    circle_rad_outer = 120
    circle_rad_inner = 30
    ring_rad = 40
    draw = ImageDraw.Draw(watermark)
    draw.ellipse([(watermark.size[0] / 2 - circle_rad_outer, watermark.size[0] / 2 - circle_rad_outer),
                  (watermark.size[0] / 2 + circle_rad_outer, watermark.size[0] / 2 + circle_rad_outer)],
                 fill=center_color, outline="black", width=2)
    draw.ellipse([(watermark.size[0] / 2 - circle_rad_inner, watermark.size[0] / 2 - circle_rad_inner),
                  (watermark.size[0] / 2 + circle_rad_inner, watermark.size[0] / 2 + circle_rad_inner)],
                 fill=(255, 255, 255), outline="black", width=1)
    draw.ellipse([(watermark.size[0] / 2 - ring_rad, watermark.size[0] / 2 - ring_rad),
                  (watermark.size[0] / 2 + ring_rad, watermark.size[0] / 2 + ring_rad)],
                 outline="black", width=1)

    watermark = set_transparency(watermark.resize((width - 2 * offset, width - 2 * offset)), transparency)

    im.paste(watermark, (offset, int((height - 2 * offset) * percent_position / 100) + offset), watermark)


def _draw_print_markers(im, offset):
    width = im.size[0]
    height = im.size[1]
    marker_length = offset * 3

    draw = ImageDraw.Draw(im)

    draw.line((0, 0, marker_length, 0), fill=(150, 150, 150), width=1)
    draw.line((0, 0, 0, marker_length), fill=(150, 150, 150), width=1)

    draw.line((width, 0, width - marker_length, 0), fill=(150, 150, 150), width=3)
    draw.line((width, 0, width, marker_length), fill=(150, 150, 150), width=3)

    draw.line((0, height, marker_length, height), fill=(150, 150, 150), width=3)
    draw.line((0, height, 0, height - marker_length), fill=(150, 150, 150), width=3)

    draw.line((width, height, width - marker_length, height), fill=(150, 150, 150), width=3)
    draw.line((width, height, width, height - marker_length), fill=(150, 150, 150), width=3)


def generate_card_front(album_details, widthpx, heightpx):
    im = Image.new('RGB', (widthpx, heightpx), (255, 255, 255))
    if 'albumArtLowRes' in album_details and album_details['albumArtLowRes'] is not None:
        theme_color = _fetch_dominant_color(album_details['albumArtLowRes'])
    else:
        theme_color = _fetch_dominant_color(album_details['albumArt'])
    _print_watermark(im, RECORD_WATERMARK, 50, 30, theme_color, 45)
    _draw_border(im, 20, 10, theme_color)
    _draw_album_art(im, album_details['albumArt'], 45, theme_color)
    _print_album_and_artist(im, album_details['albumname'], album_details['artist'], None, None, 50)
    _print_qr_code(im, album_details["songlink"], 150, 45, theme_color)
    _print_release_info(im, album_details["year"], album_details["genre"], 50, (0, 0, 0))
    _draw_print_markers(im, 20)
    return im


def _print_back_album(im, album, offset, color):
    width = im.size[0]
    draw = ImageDraw.Draw(im, 'RGBA')
    text_buffer = 10
    background_transparency = 100
    album_font = ImageFont.truetype(font_bold, 50)
    possible_chars = int((width - offset * 2) / album_font.getsize("a")[0])
    multiline_album = "\n".join(textwrap.wrap(album, possible_chars))

    draw.rectangle(
        (offset, offset, width - offset, offset + album_font.getsize_multiline(multiline_album)[1] + text_buffer * 4)
        , fill=color + (background_transparency,))

    draw.text((width / 2, offset + album_font.getsize("a")[1] + offset), multiline_album, fill=(0, 0, 0),
              font=album_font,
              align='center', anchor='ms')
    return album_font.getsize_multiline(multiline_album)[1]


def _print_tracks(im, tracks_dict, offset, album_height, color):
    width = im.size[0]
    height = im.size[1]
    draw = ImageDraw.Draw(im)

    tracks_font = ImageFont.truetype(font_regular, 40)
    tracks_italic_font = ImageFont.truetype(font_italic, 40)
    tracks_time_font = ImageFont.truetype(font_bold, 40)
    y_pointer = offset + album_height + offset
    for num, track in tracks_dict.items():
        possible_chars = int(
            (width - offset * 2 - tracks_time_font.getsize(track[1])[0] - offset / 3) / tracks_font.getsize('a')[0])
        multiline_track = "\n".join(textwrap.wrap(track[0], possible_chars))
        if y_pointer >= height - offset - tracks_font.getsize_multiline(multiline_track)[1] -offset/2:
            tracks_left_text = "and %d more..." % (len(tracks_dict) - num + 1)
            draw.text((width - offset - tracks_italic_font.getsize(tracks_left_text)[0] -
                       tracks_time_font.getsize(track[1])[0]
                       , y_pointer), tracks_left_text, fill=color, font=tracks_italic_font)
            break
        draw.text((offset, y_pointer), multiline_track, fill=color, font=tracks_font)

        draw.text((width - offset - tracks_time_font.getsize(track[1])[0], y_pointer), track[1], fill=color,
                  font=tracks_time_font)
        y_pointer = y_pointer + tracks_font.getsize_multiline(multiline_track)[1] + offset / 2


def generate_card_back(album_details, widthpx, heightpx):
    im = Image.new('RGB', (widthpx, heightpx), (255, 255, 255))
    theme_color = _fetch_dominant_color(album_details['albumArt'])
    _print_watermark(im, RECORD_WATERMARK, 35, 30, theme_color, 45)
    _draw_border(im, 20, 10, theme_color)
    album_height = _print_back_album(im, album_details['albumname'], 20, theme_color)
    _print_tracks(im, album_details["tracks"], 50, album_height, (0, 0, 0))
    _draw_print_markers(im, 20)
    return im


def generate_message_card(message, widthpx, heightpx):
    offset = 50
    im = Image.new('RGB', (widthpx, heightpx), (255, 255, 255))

    width = im.size[0]
    draw = ImageDraw.Draw(im)
    message_font = ImageFont.truetype(font_bold, 50)

    possible_chars = int((width - offset * 2) / message_font.getsize("a")[0])
    multiline_message = "\n".join(textwrap.wrap(message, possible_chars))
    draw.text((offset, offset), multiline_message, fill=(0, 0, 0), font=message_font)

    return im
