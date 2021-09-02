import json

import requests

SONGLINK_URL = "https://api.song.link/v1-alpha.1/links?url={url}"


def populate_songlink_details(album_url, album_model):
    songlink_album_url = SONGLINK_URL.format(url=album_url)
    songlink_response_json = json.loads(requests.get(songlink_album_url).content)
    print(songlink_response_json)
    album_model['entityUniqueId'] = unique_id = songlink_response_json['entityUniqueId']
    album_model['albumname'] = songlink_response_json['entitiesByUniqueId'][unique_id]['title']
    album_model['artist'] = songlink_response_json['entitiesByUniqueId'][unique_id]['artistName']
    album_model['albumArt'] = songlink_response_json['entitiesByUniqueId'][unique_id]['thumbnailUrl']
    album_model['songlink'] = songlink_response_json['pageUrl']
    album_model['linksByPlatform'] = songlink_response_json['linksByPlatform']

    album_model = _fix_youtube_albumart(album_model, songlink_response_json)
    return album_model


def _fix_youtube_albumart(album_model, songlink_response):
    if album_model['entityUniqueId'].find('YOUTUBE') > -1:
        print("Youtube Album Art link on Song.link is known to have error [%s].\nScanning through other music "
              "providers for album art" % album_model['albumArt'])
        album_model['albumArt'] = None
        for entity in songlink_response['entitiesByUniqueId']:
            if entity.find('YOUTUBE') == -1:
                album_model['albumArt'] = songlink_response['entitiesByUniqueId'][entity]['thumbnailUrl']
                print("Configured Album art url as [%s] from [%s]" % (album_model['albumArt'], entity))
                return album_model
    return album_model

