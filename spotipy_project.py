import requests
from pprint import pprint
import pandas as pd
import matplotlib as plt
import seaborn as sns

sns.set()

CLIENT_ID = '############################'
CLIENT_SECRET = '##############################'

AUTH_URL = 'https://accounts.spotify.com/api/token'

# POST

auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})

# convert response to json

auth_response_data = auth_response.json()

# save access token

access_token = auth_response_data['access_token']

headers = {

    'Authorization': 'Bearer {token}'.format(token=access_token)

}

# Base url for all spotify api endpoints

BASE_URL = 'https://api.spotify.com/v1/'

track_id = '3lJjySbUdugEbx3j3TM1Au'

# actual get request with proper header

r = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)

r = r.json()

pprint(r)
print('\n\n')

artist_id = '6emrXi84Xjdb8YcEm82XEZ'

# pull all artists albums

r = requests.get(BASE_URL + 'artists/' + artist_id + '/albums', headers=headers,
                 params={'include_groups': 'album', 'limit': 50})

d = r.json()

albums = []

data = []

for album in d['items']:
    # pprint(album)
    album_name = album['name']
    print(album['name'] + '----' + album['release_date'])

    trim_name = album['name'].split('(')[0].strip()
    if trim_name.upper() in albums or int(album['release_date'][:4]) < 1983:
        continue
    albums.append(trim_name.upper())

    print(album_name)

    t = requests.get(BASE_URL + 'albums/' + album['id'] + '/tracks', headers=headers)

    tracks = t.json()['items']

    for track in tracks:
        f = requests.get(BASE_URL + 'audio-features/' + track['id'], headers=headers)

        f = f.json()

        f.update({
            'track_name': track['name'],
            'album_name': album_name,
            'short_album_name': trim_name,
            'release_date': album['release_date'],
            'album_id': album['id']
        })

        data.append(f)

df = pd.DataFrame(data)

# convert release date to an actual date, and sort by it

df['release_date'] = pd.to_datetime(df['release_date'])

df = df.sort_values(by='release_date')

df = df.query('short_album_name != "Right Now Right Now"')

df = df[~df['track_name'].str.contains('Live|Mix|Track')]

print(df.head())

ax = plt.scatter(data=df, x='valence', y='acousticness',
                 hue='short_album_name', palette='rainbow',
                 size='duration_ms', sizes=(50, 1000),
                 alpha=0.7)

# display legend without 'size' attribute
h, labs = ax.get_legend_handles_labels()
ax.legend(h[1:10], labs[1:10], loc='best', title=None)