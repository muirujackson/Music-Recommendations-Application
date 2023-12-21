from flask import Blueprint, render_template, redirect, session, request, jsonify, url_for
import requests
from functools import wraps
import os
from dotenv import load_dotenv
from urllib.parse import urlencode
from helpers.spotify_helpers import check_session_validity, refresh_token

"""
redirect, session, url_for
from helpers.spotify_helpers import fetch_liked_songs, other_custom_function
"""

main_blueprint = Blueprint('main', __name__)

# Load environment variables from .env
load_dotenv()


@main_blueprint.route('/', strict_slashes=False)
@check_session_validity
def index():
    access_token = session.get('access_token')

    # Endpoint URL for the Global Top 50 playlist
    # playlist_url = 'https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M'
    playlist_url = 'https://api.spotify.com/v1/playlists/37i9dQZEVXbMDoHDwVN2tF'

    # Headers containing the access token
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Make a GET request to the Spotify API endpoint
    if access_token is not None:
        response = requests.get(playlist_url, headers=headers)

        if response.status_code == 200:
            # Extract playlist details from the response
            playlist_data = response.json()
            # Process playlist data as needed
            return render_template('index.html', playlist_data=playlist_data)
        else:
            refresh_token()
            return f"Failed to retrieve playlist: {response.status_code} - {response.text}"
    else:
        return render_template('index.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)

    return decorated_function


# Route for handling search results
@main_blueprint.route('/search', methods=['GET'], endpoint='search_results')
def search_results():
    query = request.args.get('query')  # Get the search query from the form

    search_url = 'https://api.spotify.com/v1/search'

    params = {
        'q': query,
        'type': 'track',  # Search for tracks
        'limit': 10  # Limit the number of results to 10
        # You may include other parameters as needed (e.g., market, offset, etc.)
    }

    access_token = session.get('access_token')

    if access_token:
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            response = requests.get(search_url, params=params, headers=headers)
            response.raise_for_status()  # Raise an error for HTTP errors (status codes >= 400)

            search_results = response.json()
            items = search_results.get('tracks', {}).get('items', [])

            return render_template('search_results.html', items=items, query=query)

        except requests.HTTPError as http_err:
            return f"HTTP error occurred: {http_err}"

        except Exception as err:
            return f"An error occurred: {err}"

    else:
        return "User is not logged in or access token is missing"


@main_blueprint.route('/dashboard', strict_slashes=False)
@login_required
def dashboard():
    access_token = session.get('access_token')
    headers = {
        'Authorization': 'Bearer ' + access_token
    }

    # Fetch a user's saved tracks (liked songs)
    saved_tracks_url = 'https://api.spotify.com/v1/me/tracks'
    response = requests.get(saved_tracks_url, headers=headers)

    if response.status_code == 200:
        total_liked_songs = response.json()['total']
        saved_tracks_data = response.json()['items']
        return render_template('dashboard.html', total_liked_songs=total_liked_songs, saved_tracks=saved_tracks_data)
    else:
        return "Failed to fetch saved tracks"

    """
    :return:
    ""ample usage of functions from spotify_helpers.py
    #liked_songs = fetch_liked_songs()
    result = other_custom_function()
    # ..."""
    # return render_template('dashboard.html')


@main_blueprint.route("/login", strict_slashes=False)
def login():
    params = {
        'client_id': os.environ.get('CLIENT_ID'),
        'response_type': 'code',
        'redirect_uri': os.environ.get('REDIRECT_URI'),
        'scope': os.environ.get('SCOPE')
    }
    auth_url = f"{os.environ.get('AUTH_URL')}?{urlencode(params)}"
    return redirect(auth_url)


@main_blueprint.route("/callback", strict_slashes=False)
def callback():
    # Handle callback from Spotify's API after user authentication
    code = request.args.get('code')

    if code:
        # Exchange authorization code for access token
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': os.environ.get('REDIRECT_URI'),
            'client_id': os.environ.get('CLIENT_ID'),
            'client_secret': os.environ.get('CLIENT_SECRET')
        }

        # Make a POST request to Spotify's token endpoint
        response = requests.post(os.environ.get('TOKEN_URL'), data=payload)

        if response.status_code == 200:
            # Access token received successfully
            access_token = response.json().get('access_token')

            # Store the access token in the session
            session['access_token'] = access_token

            # Redirect to a page where you want to go after successful login
            return redirect(url_for('main.index'))  # Replace 'dashboard' with your desired endpoint
        else:
            # Handle error response from Spotify API (e.g., log the error)
            error_message = response.json().get('error_description')
            return f"Error: {error_message}"
    else:
        # Handle the case where 'code' is not present in the callback URL
        return "Error: Authorization code not received"


@main_blueprint.route("/logout", strict_slashes=False)
def logout():
    session.clear()  # Clear session data
    # Redirect to the homepage or a login page
    return redirect(url_for('main.index'))


@main_blueprint.route('/recommendation', methods=['GET'], strict_slashes=False)
def recommendation():
    access_token = session.get('access_token')  # Get the user's access token (ensure it's retrieved properly)

    if access_token:
        headers = {
            'Authorization': 'Bearer ' + access_token
        }

        # Fetch a user's saved tracks (liked songs)
        saved_tracks_url = 'https://api.spotify.com/v1/me/tracks'
        response = requests.get(saved_tracks_url, headers=headers)

        if response.status_code == 200:
            # Extract the track IDs of liked songs
            liked_songs = [track['track']['id'] for track in response.json()['items']]

            # Recommendation endpoint URL
            recommendation_endpoint = 'https://api.spotify.com/v1/recommendations'

            # Data to be sent to the recommendation endpoint
            data = {
                'seed_tracks': liked_songs,
                # Include other necessary data for recommendations (e.g., market, limit, etc.)
            }

            # Send the data to the recommendation endpoint
            recommendation_response = requests.get(recommendation_endpoint, headers=headers, params=data)

            if recommendation_response.status_code == 200:
                # Successfully received recommended songs from Spotify
                recommendation_data = recommendation_response.json()
                recommended_songs = recommendation_data.get('tracks', [])

                # Return the recommended songs as JSON
                return jsonify({'recommended_songs': recommended_songs})
            else:
                return jsonify(
                    {'message': f"Failed to fetch recommendations: {recommendation_response.status_code}"}), 500
        else:
            return jsonify({'message': f"Failed to fetch liked songs: {response.status_code}"}), 500
    else:
        return jsonify({'message': 'Access token not found'}), 401

@main_blueprint.route('/like-song', methods=['POST'], strict_slashes=False)
def like_song():
    access_token = session.get('access_token')
    track_id = request.form['track_id']

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    add_to_library_url = f'https://api.spotify.com/v1/me/tracks?ids={track_id}'
    response = requests.put(add_to_library_url, headers=headers)

    if response.status_code == 200:
        return jsonify({'message': 'Song added to liked songs!'})
    else:
        print(track_id)
        return jsonify({'error': 'Failed to add song to liked songs.'}), response.status_code
    # access_token = session.get('access_token')  # Replace with your access token
    # track_id = request.form['track_id']
    #
    # headers = {
    #     'Authorization': 'Bearer ' + access_token,
    #     'Content-Type': 'application/json'
    # }
    #
    # # Add the track to the user's library (liked songs)
    # add_to_library_url = f'https://api.spotify.com/v1/me/tracks?ids={track_id}'
    # response = requests.put(add_to_library_url, headers=headers)
    #
    # if response.status_code == 200:
    #
    #     return print('Song added to liked songs!')
    # if request.method == 'POST':
    #     track_id = request.form.get('track_id')  # Get the track ID from the POST request
    #     # Add logic to handle adding the track to the liked playlist
    #     # This could involve interacting with the Spotify API or your database
    #
    #     # For testing purposes, you can print a message to see if the route is accessed
    #     print(f"Adding track {track_id} to liked songs.")
    #
    #     # Return a response (optional)
    #     return "Song liked successfully"  # You can customize this response as needed
    # else:
    #     return "Invalid request method"
    # print(3)
    # return 'Failed to add song to liked songs'


# Define a context processor function for the blueprint
@main_blueprint.app_context_processor
def common_variables():
    common_var = "This is a common variable in the blueprint context"
    # Accessing the stored access token
    access_token = session.get('access_token')
    if access_token is not None:
        logged_in = True
    else:
        logged_in = False
    return {'logged_in': logged_in, 'access_token': access_token}
