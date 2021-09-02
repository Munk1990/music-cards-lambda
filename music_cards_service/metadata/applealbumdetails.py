import requests
import json


def populate_apple_details(albumid, albumdetails):
    print("Querying apple for album : %s" % albumid)
    appleurl = "https://itunes.apple.com/lookup?entity=song&id=" + albumid
    appleresponse = requests.get(appleurl)
    print(appleurl)
    applejson = json.loads(appleresponse.content)
    try:
        albumdetails['year'] = applejson['results'][0]['releaseDate'][0:4]
    except IndexError:
        print("Unable to get Release Date from json:[%s]" % applejson['results'][0])
        albumdetails['year'] = None

    try:
        albumdetails['genre'] = applejson['results'][0]['primaryGenreName']
    except IndexError:
        print("Unable to get Genre Date from json:[%s]" % applejson['results'][0])
        albumdetails['genre'] = None
    albumdetails['tracks'] = find_album_tracks(applejson['results'])
    return albumdetails


def pretty_time_from_ms(millis):
    s = millis / 1000
    hours, remainder = divmod(s, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours == 0:
        return '{:02}:{:02}'.format(int(minutes), int(seconds))
    else:
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


def find_album_tracks(results):
    tracks = {}
    for item in results:
        if item['wrapperType'] == "track":
            tracks[item['trackNumber']] = (item['trackName'], pretty_time_from_ms(item['trackTimeMillis']))
    return tracks
