from flask import Flask, redirect, session, request
import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlencode

app = Flask(__name__)

# Load environment variables from .env
load_dotenv()

app.secret_key = os.environ.get('CLIENT_SECRET')


@app.route('/', strict_slashes=False)
def index():  # put application's code here
    return 'Hello World!'


@app.route("/login")
def login():
    params = {
        'client_id': os.environ.get('CLIENT_ID'),
        'response_type': 'code',
        'redirect_uri': os.environ.get('REDIRECT_URI'),
        'scope': os.environ.get('SCOPE')
    }
    auth_url = f"{os.environ.get('AUTH_URL')}?{urlencode(params)}"
    return redirect(auth_url)


@app.route("/callback")
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
            return "worked"  # Replace 'dashboard' with your desired endpoint
        else:
            # Handle error response from Spotify API (e.g., log the error)
            error_message = response.json().get('error_description')
            return f"Error: {error_message}"
    else:
        # Handle the case where 'code' is not present in the callback URL
        return "Error: Authorization code not received"


if __name__ == '__main__':
    app.run(debug=True)
