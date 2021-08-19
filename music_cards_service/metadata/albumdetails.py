import requests
import json


def pretty_time_from_ms(millis):
    s = millis/1000
    hours, remainder = divmod(s, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours == 0:
        return '{:02}:{:02}'.format(int(minutes), int(seconds))
    else :
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


def find_album_tracks(results):
    tracks = {}
    for item in results:
        if item['wrapperType'] == "track":
            tracks[item['trackNumber']] = (item['trackName'], pretty_time_from_ms(item['trackTimeMillis']))
    return tracks


def search_songlink_album(albumid):
    print("Querying songlink for album : %s" % str(albumid))
    if albumid in []:
        songlinkurl = "https://api.song.link/v1-alpha.1/links?type=album&userCountry=US&platform=appleMusic&id=" + str(
            albumid)
        appleurl = "https://itunes.apple.com/lookup?entity=song&id=" + str(albumid)
    else:
        songlinkurl = "https://api.song.link/v1-alpha.1/links?type=album&userCountry=IN&platform=appleMusic&id=" + str(
            albumid)
        appleurl = "https://itunes.apple.com/lookup?entity=song&country=IN&id=" + str(albumid)
    response = requests.get(songlinkurl)
    jsonresponse = json.loads(response.content)
    print(jsonresponse)
    albumdetails = {}
    unique_id = jsonresponse['entityUniqueId']
    albumdetails['albumname'] = jsonresponse['entitiesByUniqueId'][unique_id]['title']
    albumdetails['artist'] = jsonresponse['entitiesByUniqueId'][unique_id]['artistName']
    albumdetails['albumArt'] = jsonresponse['entitiesByUniqueId'][unique_id]['thumbnailUrl']
    albumdetails['songlink'] = jsonresponse['pageUrl']

    appleresponse = requests.get(appleurl)
    print(appleurl)
    applejson = json.loads(appleresponse.content)
    try:
        albumdetails['year'] = applejson['results'][0]['releaseDate'][0:4]
    except IndexError:
        print("Unable to get Release Date from json:[%s]" % applejson['results'][0])
        albumdetails['year'] = ""

    try:
        albumdetails['genre'] = applejson['results'][0]['primaryGenreName']
    except IndexError:
        print("Unable to get Genre Date from json:[%s]" % applejson['results'][0])
        albumdetails['genre'] = ""
    albumdetails['tracks'] = find_album_tracks(applejson['results'])

    return albumdetails




