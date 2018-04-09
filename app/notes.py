# ToDo
# - Multiuser setup (use session key or something auth-related as new roots in NOTE_STORE. Grab that in get_notes()

from typing import List

import flask
import io
from bs4 import BeautifulSoup

import google.oauth2.credentials
import googleapiclient.discovery
from googleapiclient.http import MediaIoBaseDownload


API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

NOTE_STORE = {}


def update_notes():
    def extract_notes_from_html(html: str) -> List[str]:
        soup = BeautifulSoup(html, 'html.parser')
        note_tables = soup.select('table table')
        quotes = []
        for note in note_tables:
            quote_element = note.select('td:nth-of-type(2) span')[0]
            text = quote_element.contents[0]
            quotes.append(text)
        return quotes

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    drive_service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Get Notes Folder ID
    notes_folder_search = drive_service.files().list(
        q="name='Play Books Notes'"
    ).execute()

    if notes_folder_search:
        files = notes_folder_search.get('files')
        if len(files) > 0:
            notes_folder_id = files[0].get('id')

    # Get Notes IDs
    notes = drive_service.files().list(
        q=f"'{notes_folder_id}' in parents"
    ).execute()

    # for note in notes.get('files'):
    for note in notes.get('files'):
        note_id = note.get('id')
        book_name = note.get('name')
        book_name = book_name.replace('Notes from "', '').replace('Notizen aus "', '')[:-1]

        # Download notes as HTML
        note_file = drive_service.files().export_media(fileId=note_id,
                                                       mimeType='text/html')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, note_file)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {book_name} {int(status.progress()*100)}%.")

        # Extract note text from raw html
        raw_html = fh.getvalue().decode("utf-8")
        final_notes = extract_notes_from_html(raw_html)

        # Add to note store
        NOTE_STORE[note_id] = {
            'id': note_id,
            'book_name': book_name,
            'notes': final_notes,
            'note_count': len(final_notes),
        }


def get_notes(user=None):
    if NOTE_STORE:
        return NOTE_STORE
    update_notes()
    return NOTE_STORE
