# PlayBooksNotes
API &amp; Frontend for getting your annotations and quotes from the Google Play Books App.

The app exposes a JSON API for building arbitrary frontends / clients. To be fancy, it also implements a very simple frontend, a web page which displays all your quotes in a slider as seen in the screenshot.

### What is this useful for?
Background info: When using the [Google Play Books app](https://play.google.com/store/apps/details?id=com.google.android.apps.books&hl=en) for reading ebooks, you can annotate sentences. Those annotations and quotes get stored in your Google Drive in an Google Doc which is automatically updated.

Could be used for:
- New Tab page in your favorite web browser
- Chromecast Backdrop
- "Quote Of The Day" widget on your phone
- Amazon Alexa Skill

<img width="1680" alt="screen shot 2018-04-08 at 22 11 52" src="https://user-images.githubusercontent.com/3121306/38472156-d7cda50a-3b7b-11e8-9ca0-541296755118.png">

### How to self host this:
- Install dependencies (`pipenv install`)
- Create Google API Project
- Setup OAuth (callback URL: /oauth2callback)
- Download `client_id.json` and `client_secret.json` from the API Console
- Run the flask app
