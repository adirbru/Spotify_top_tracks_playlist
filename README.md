# Spotify_top_tracks_playlist
## Obtain the credentials
1. Go to https://developer.spotify.com/console/post-playlists/, and click the Get Token button at the end of the page.
2. Check both `playlist-modify-public` and `playlist-modify-private` 
3. Open your browser dev-tools (F12 on Chrome for Windows/Command-Option-J on Chrome for Mac)
4. Find the `/authorize` request and obtain the following:
* `sp_dc` and `sp_key` cookies from the request headers cookies.
* `client_id` from the url parameters
5. `user_id` from https://www.spotify.com/us/account/overview/?utm_source=spotify&utm_medium=menu&utm_campaign=your_account
6. Insert all to the code parameters and run the python code.
