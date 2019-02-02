# ToDo
# - Multiuser setup (use session key or something auth-related as new roots in NOTE_STORE. Grab that in get_notes()
import random
from typing import List

import flask
import io

import os
from bs4 import BeautifulSoup

import google.oauth2.credentials
import googleapiclient.discovery
from flask import logging
from googleapiclient.http import MediaIoBaseDownload

from exceptions import PlayBooksFolderNotFound

API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

NOTE_STORE = {}

def update_notes():
    global NOTE_STORE
    def extract_notes_from_html(html: str) -> List[str]:
        soup = BeautifulSoup(html, 'html.parser')
        note_tables = soup.select('table table')
        quotes = []
        for note in note_tables:
            element_dict = {}
            quote_element = note.select('td:nth-of-type(2) span')[0]
            quote = quote_element.contents[0]
            print('Quote: ' + quote[:10])
            chapter = quote_element.find_previous('h2').contents[0].contents[0]
            element_dict['quote'] = quote
            element_dict['chapter'] = chapter
            quotes.append(element_dict)
        return quotes

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    drive_service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Get Notes Folder ID
    notes_folder_search = drive_service.files().list(
        q="name='Play Books Notes'"
    ).execute()

    files = notes_folder_search.get('files')
    if len(files) < 1:
        raise PlayBooksFolderNotFound()
    notes_folder_id = files[0].get('id')

    # Get Notes IDs
    notes = drive_service.files().list(
        q=f"'{notes_folder_id}' in parents"
    ).execute()

    files_to_download = notes.get('files')

    # only download 2 books when developing
    from app import app
    if os.environ.get('FLASK_DEBUG'):
        files_to_download = files_to_download[:5]

    for note in files_to_download:
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

        # Add to note store if the book has notes
        if len(final_notes):
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


def get_random_note(user=None):
    if not NOTE_STORE:
        update_notes()

    quote_tuples = [(note, book.copy()) for book in NOTE_STORE.values() for note in book['notes']]
    note, book = random.choice(quote_tuples)
    # replace book notes with the single note we randomly chose
    book['notes'] = [note]
    return {book['id']: book}
