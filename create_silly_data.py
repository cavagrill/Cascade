import cavaconn as cc
import pandas as pd
import requests

def get_artist_id(artistname):
    r = requests.get('https://api.spotify.com/v1/search?q={}&type=artist'.format(artistname))
    results = r.json()
    return results['artists']['items'][0]['id']

def get_artist(artist):
    r = requests.get('https://api.spotify.com/v1/artists/{}'.format(artist))
    results = r.json()
    art = {'followers':results['followers']['total'],
               'name':     results['name'],
               'genres':   results['genres'],
               'id':       results['id'],
               'popularity': results['popularity']}
    return art

def get_albums(artist):
    r = requests.get('https://api.spotify.com/v1/artists/{}/albums'.format(artist))
    results = r.json()
    albumns = []
    tracks  = []
    for albumn in results['items']:
        albumns.append({'name':albumn['name'],
                        'marketsize': len(albumn['available_markets']),
                        'id':albumn['id'],
                        'artists':artist}) 
        tracks += get_tracks(albumn['id'])
    return albumns,tracks

def get_tracks(album):
    r = requests.get('https://api.spotify.com/v1/albums/{}/tracks'.format(album))
    results = r.json()
    tracks  = []
    for track in results['items']:
        tracks.append({'duration':track['duration_ms'],
                       'explicit':track['explicit'],
                       'track_number':track['track_number'],
                       'album':album,
                       'trackid':track['id']})
    return tracks



artistsat930 = ['Chvrches','Tribal+Seeds','Good+Charlotte','Tokyo+Police+Club','Dirtyphonics&Funtcase','Murder+By+Death',
                'Penguin+Prison','Titus+Andronicus','Parquet+Courts','Animal+Collective',
                'Caveman','The+Sonics','Young+Thug','M.+Ward','Slander',
                'Puddles+Pity+Party','Bob+Mould','Elephant+Revival']
artists1 = [] 
albums = []
tracks = []
for artist in artistsat930:
    artist_id = get_artist_id(artist)
    artists1.append(get_artist(artist_id))
    artist_info = get_albums(artist_id)
    albums += artist_info[0]
    tracks += artist_info[1]

arts = pd.DataFrame(artists1)
albumns = pd.DataFrame(albums)
tracks_pd = pd.DataFrame(tracks)
eng = cc.get_engine('server_info.yml', 'test_tables')
arts.to_sql('artists',eng,if_exists='replace')
albumns.to_sql('albums',eng,if_exists='replace')
tracks_pd.to_sql('tracks',eng,if_exists='replace')
