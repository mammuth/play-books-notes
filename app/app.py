# -*- coding: utf-8 -*-

import os

import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow

from flask import render_template, redirect, request, url_for
from flask_cache import Cache

import notes

app = flask.Flask(__name__)
app.secret_key = 'REPLACE ME - this value is here as a placeholder.'  # ToDo secret key

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

if os.environ.get('SERVER_NAME'):
    app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME')

ROOT_PATH = os.path.join(app.root_path, '')

CLIENT_SECRETS_FILE = f"{ROOT_PATH}client_secret.json"  # Download that file from the Google API Console

OAUTH_SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
]

def is_cache():
    return True if request.query_string.decode('utf-8') == 'cache=False' else False

@app.route('/')
def index():
    return redirect(url_for('list_notes'))


@app.route('/update')
def update():
    notes.update_notes()
    return redirect(url_for('list_notes'))


@app.route('/random-note')
@cache.cached(unless=is_cache)
def random_note():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    context = {
        'notes': notes.get_random_note(),
        'is_single': True
    }
    return render_template('notes.html', **context)


# ToDo
# - Use same view but behave according to accepted content-type header
# - Display total number of quotes
@app.route('/notes')
@cache.cached(unless=is_cache)
def list_notes():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    context = {
        'notes': notes.get_notes(),
    }
    return render_template('notes.html', **context)


# ToDo
# - Don't only parse and store quote text, but also chapter title and page number
@app.route('/notes-api')
@cache.cached(unless=is_cache)
def list_notes_api():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    return flask.jsonify(**notes.get_notes())


@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=OAUTH_SCOPES)

    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=OAUTH_SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('list_notes'))


@app.route('/revoke')
def revoke():
    if 'credentials' not in flask.session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return 'Credentials successfully revoked.'
    else:
        return 'An error occurred.'


@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return 'Credentials have been cleared.<br><br>'


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    # Allow OAUTH to work without TLS for development
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('0.0.0.0', 8080, debug=True)
