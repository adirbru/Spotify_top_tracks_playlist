import requests
import json
import pandas
import datetime
import re
import logging
import sys
import urllib3
urllib3.disable_warnings()

SP_DC = ''
SP_KEY = ''
USER_ID = ''
CLIENT_ID = ''

COOKIES = f'sp_dc={SP_DC};sp_key={SP_KEY};'
PERIOD = 'short_term'
MAX_SONGS = 50

SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_URL = 'https://api.spotify.com/v1'
TOP_TRACKS_URL = '/me/top/tracks'
PLAYLISTS_URL = '/users/{user}/playlists'
PLAYLISTS_SONGS_URL = '/playlists'
CREATE_PLAYLIST_SCOPES = ['playlist-modify-public', 'playlist-modify-private']
PLAYLIST_FORMAT = 'Your {number} most popular songs on {date}!'

def get_tracks(session, max_songs, period):	
	response = session.get(f'{SPOTIFY_URL}{TOP_TRACKS_URL}?limit={max_songs}&time_range={period}')
	if response.status_code == 200:
		tracks_df = pandas.DataFrame(response.json()['items'])
		logger.info(f"Acquired {max_songs} liked tracks successfully")
		return tracks_df
	else:
		logger.info("Failed getting liked songs")	
		raise IOError


def create_playlist(session, user, playlist_name):
	data = {
			  "name": playlist_name,
			  "description": "Automated playlist",
			  "public": 'false'
			}
	response = session.post(f'{SPOTIFY_URL}{PLAYLISTS_URL.format(user=user)}', data=json.dumps(data))
	if response.status_code == 201:
		logger.info("Created playlist successfully")
	else:
		logger.info("Failed creating playlist")	
		raise IOError
	return json.loads(response.content)

def add_songs_to_playlist(session, playlist_id, songs_uris):
	for song_uri in songs_uris:
		session.post(f'{SPOTIFY_URL}{PLAYLISTS_SONGS_URL}/{playlist_id}/tracks?uris={song_uri.replace(":", "%3A")}')
	logger.info(f"Successfully uploaded {len(songs_uris)} songs to the playlist!")


def create_session(api_key):
	session = requests.session()
	session.verify = False
	session.headers['Accept'] = 'application/json'
	session.headers['Content-Type'] = 'application/json'
	session.headers['Authorization'] = f'Bearer {api_key}'
	logger.info("Session created successfully")
	return session

def get_token(cookies, client_id):
	response = requests.get(f"{SPOTIFY_TOKEN_URL}?response_type=token&redirect_uri=https%3A%2F%2Fdeveloper.spotify.com%2Fcallback&client_id={client_id}&scope={'+'.join(CREATE_PLAYLIST_SCOPES)}&state=1axu4p", verify=False, allow_redirects=False, headers={'cookie':cookies}).headers.get('location')
	if response:
		logger.info("Acquired token successfully")
	else:
		logger.info("Failed getting token")	
		raise IOError
	return re.findall('#access_token=([^&]+)', response)[0]

def main():
	logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
	logger = logging.getLogger('Spotify')
	api_key = get_token(COOKIES, CLIENT_ID)
	session = create_session(api_key)
	tracks = get_tracks(session, MAX_SONGS, PERIOD)
	today = datetime.datetime.now().strftime('%Y-%m-%d')
	playlist_json = create_playlist(session, USER_ID, PLAYLIST_FORMAT.format(number=MAX_SONGS, date=today))
	add_songs_to_playlist(session, playlist_json['id'], tracks['uri'].values.tolist())

if __name__ == '__main__':
	main()