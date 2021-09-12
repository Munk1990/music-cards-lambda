import json

import requests

SONGLINK_URL = "https://api.song.link/v1-alpha.1/links?url={url}"
SONGLINK_ID = "https://api.song.link/v1-alpha.1/links?type=album&platform={platform}&id={albumid}"


def populate_songlink_details_from_album(provider, albumid, album_model):
    album_url = SONGLINK_ID.format(platform=provider, albumid=albumid)
    response_json = json.loads(requests.get(album_url).content)
    print(response_json)
    return _process_json(response_json, album_model)


def populate_songlink_details_from_url(album_url, album_model):
    songlink_album_url = SONGLINK_URL.format(url=album_url)
    response_json = json.loads(requests.get(songlink_album_url).content)
    print(response_json)
    return _process_json(response_json, album_model)


def _process_json(response_json, album_model):
    album_model['entityUniqueId'] = unique_id = response_json['entityUniqueId']
    album_model['albumid'] = unique_id.split("::")[1]
    album_model['albumidtype'] = response_json['entitiesByUniqueId'][unique_id]["platforms"][0]
    album_model['albumname'] = response_json['entitiesByUniqueId'][unique_id]['title']
    album_model['artist'] = response_json['entitiesByUniqueId'][unique_id]['artistName']
    album_model['albumArt'] = response_json['entitiesByUniqueId'][unique_id]['thumbnailUrl']
    album_model['songlink'] = response_json['pageUrl']
    album_model['linksByPlatform'] = response_json['linksByPlatform']
    album_model = _fix_youtube_albumart(album_model, response_json)
    return album_model


def _fix_youtube_albumart(album_model, response):
    if album_model['entityUniqueId'].find('YOUTUBE') > -1:
        print("Youtube Album Art link on Song.link is known to have error [%s].\nScanning through other music "
              "providers for album art" % album_model['albumArt'])
        album_model['albumArt'] = None
        for entity in response['entitiesByUniqueId']:
            if entity.find('YOUTUBE') == -1:
                album_model['albumArt'] = response['entitiesByUniqueId'][entity]['thumbnailUrl']
                print("Configured Album art url as [%s] from [%s]" % (album_model['albumArt'], entity))
                return album_model
    return album_model
