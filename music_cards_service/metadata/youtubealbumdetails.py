import json
import re

import requests

PLAYLIST_LISTITEMS_URL = "https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=50&playlistId={playlistid}&key={key}"
TRACKDETAILS_URL = "https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id={trackid}&key={key}"


def populate_youtube_details(album_id, albumdetails, apikey):
    playlist_request_url = PLAYLIST_LISTITEMS_URL.format(playlistid=album_id,
                                                         key=apikey)
    response = requests.get(playlist_request_url)
    jsonresponse = json.loads(response.content)
    print("Youtube playlist response [%s] from URL [%s]" % (jsonresponse, playlist_request_url))
    first_track_description = jsonresponse['items'][0]['snippet']['description']
    release_year_arr = regex_groups(first_track_description, r'Released on: (\d\d\d\d)')
    albumdetails['albumArtLowRes'] = jsonresponse['items'][0]['snippet']['thumbnails']['default']['url']
    if albumdetails['albumArt'] is None:
        albumdetails['albumArt'] = get_playlist_thumbnail(jsonresponse['items'][0]['snippet']['thumbnails'])
    if len(release_year_arr) > 0:
        albumdetails['year'] = release_year_arr[0]
    else:
        print("Unable to find Release date, in description field. Replacing with published date of first track")
        albumdetails['year'] = regex_groups(jsonresponse['items'][0]['snippet']['publishedAt'], r'\d\d\d\d')[0]

    albumdetails['tracks'] = find_album_tracks(jsonresponse['items'], apikey)
    if albumdetails['genre'] is None:
        albumdetails['genre'] = 'YouTube'
    return albumdetails


def regex_groups(text, pattern):
    results = re.findall(pattern, text)
    return results


def find_album_tracks(results, apikey):
    tracks = {}
    track_list = list(map(lambda result: result['contentDetails']['videoId'], results))
    tracks_csv = ",".join(track_list)
    tracks_response = json.loads(requests.get(TRACKDETAILS_URL.format(trackid=tracks_csv, key=apikey)).content)
    tracks_result = tracks_response['items']
    for counter in range(len(tracks_result)):
        result = tracks_result[counter]
        track_title = result['snippet']['title']
        track_length = pretty_time_format(result['contentDetails']['duration'])
        tracks[counter] = (track_title, track_length)
    return tracks


def pretty_time_format(youtube_time):
    hours_matches = regex_groups(youtube_time, r'(\d+)H')
    if len(hours_matches) > 0:
        hours = int(hours_matches[0])
    else:
        hours = 0
    mins_matches = regex_groups(youtube_time, r'(\d+)M')
    if len(mins_matches) > 0:
        mins = int(mins_matches[0])
    else:
        mins = 0
    seconds_matches = regex_groups(youtube_time, r'(\d+)S')
    if len(seconds_matches) > 0:
        seconds = int(seconds_matches[0])
    else:
        seconds = 0
    if hours == 0:
        return '{:02}:{:02}'.format(mins, seconds)
    else:
        return '{:02}:{:02}:{:02}'.format(hours, mins, seconds)


def get_playlist_thumbnail(thumbnails):
    for count in range(len(thumbnails) - 1, 0, -1):
        return list(thumbnails.values())[count]['url']
