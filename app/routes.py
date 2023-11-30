from flask import Blueprint, render_template, redirect, session, request, url_for
import requests
from functools import wraps
import os
from dotenv import load_dotenv
from urllib.parse import urlencode
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


from helpers.spotify_helpers import check_session_validity

"""
redirect, session, url_for
from helpers.spotify_helpers import fetch_liked_songs, other_custom_function
"""

main_blueprint = Blueprint('main', __name__)

# Load environment variables from .env
load_dotenv()

# Spotify credentials
client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')

# Authenticate with Spotify
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

@main_blueprint.route('/', strict_slashes=False)
@check_session_validity
def index():

    return render_template('index.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            return redirect(url_for('login'))
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
def dashboard():
    """
    :return:
    ""ample usage of functions from spotify_helpers.py
    #liked_songs = fetch_liked_songs()
    result = other_custom_function()
    # ..."""
    return "Dashboard content here"


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


# Define a context processor function for the blueprint
@main_blueprint.app_context_processor
def common_variables():
    common_var = "This is a common variable in the blueprint context"
    # Accessing the stored access token
    a_token = session.get('access_token')
    if a_token is not None:
        logged_in = True
    else:
        logged_in = False
    return {'logged_in': logged_in, 'a_token': a_token}


