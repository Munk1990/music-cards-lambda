import json
import re

from metadata.applealbumdetails import populate_apple_details
from metadata.songsearchalbumdetails import populate_songlink_details
from metadata.youtubealbumdetails import populate_youtube_details

albumdetailsmodel = {}
albumdetailsmodel['albumname'] = None
albumdetailsmodel['artist'] = None
albumdetailsmodel['albumArt'] = None
albumdetailsmodel['songlink'] = None
albumdetailsmodel['albumid'] = None
albumdetailsmodel['albumidtype'] = None

albumdetailsmodel['year'] = None
albumdetailsmodel['genre'] = None
albumdetailsmodel['tracks'] = {}


def new_album():
    return albumdetailsmodel.copy()


def fetch_id_from_entityid(entityUniqueId):
    return re.findall('::(.*)', entityUniqueId)[0]


def populate_album(album_url, youtube_key):
    albumdetails = new_album()
    print("Querying songlink for album url [%s]" % album_url)
    albumdetails = populate_songlink_details(album_url, albumdetails)
    print("Albumdetails pre youtube:[%s]" % albumdetails)
    if 'appleMusic' in albumdetails['linksByPlatform']:
        print("Querying youtube for album url [%s]" % album_url)
        applealbumid = fetch_id_from_entityid(albumdetails['linksByPlatform']['appleMusic']['entityUniqueId'])
        albumdetails = populate_apple_details(applealbumid, albumdetails)
    print("[%s][%s][%s]" % ('youtubeMusic' in albumdetails['linksByPlatform'], albumdetails['year'] is None,len(albumdetails['tracks']) == 0))
    if 'youtubeMusic' in albumdetails['linksByPlatform'] and (
            albumdetails['year'] is None or len(albumdetails['tracks']) == 0):
        if youtube_key is None or len(youtube_key.strip()) == 0:
            raise Exception("Youtube API missing. Can not process information from Google")
        else:
            print("Querying youtube for album url [%s]" % album_url)
            youtubealbumid = fetch_id_from_entityid(albumdetails['linksByPlatform']['youtubeMusic']['entityUniqueId'])
            albumdetails = populate_youtube_details(youtubealbumid, albumdetails, youtube_key)
    print("Populated albumdetails json [%s]" % json.dumps(albumdetails, indent=4))
    if albumdetails['genre'] is None:
        albumdetails['genre'] = albumdetails['albumidtype']
    return albumdetails

