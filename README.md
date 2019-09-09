# Play Books Notes

<a href="https://www.buymeacoffee.com/mammuth" target="_blank"><img src="https://bmc-cdn.nyc3.digitaloceanspaces.com/BMC-button-images/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>

API &amp; Frontend for exporting your annotations and quotes from the Google Play Books App.

The app exposes a JSON API for building arbitrary frontends / clients with the exported notes. To be fancy, it also implements a very simple frontend, a web page which displays all your quotes in a slider as seen in the screenshot.

## What is this useful for?
Background info: When using the [Google Play Books app](https://play.google.com/store/apps/details?id=com.google.android.apps.books&hl=en) for reading ebooks, you can annotate sentences. Those annotations and quotes get stored in your Google Drive in an Google Doc which is automatically updated.

Could be used for:
- New Tab page in your browser (using eg. this [Chrome Extension](https://github.com/jimschubert/newtab-redirect/wiki))
- Chromecast Backdrop
- "Quote Of The Day" widget on your phone
- Amazon Alexa Skill
- Export your notes for backup purposes

<img width="1680" alt="screen shot 2018-04-08 at 22 11 52" src="https://user-images.githubusercontent.com/3121306/38472156-d7cda50a-3b7b-11e8-9ca0-541296755118.png">

## Usage

You need to create a Google Cloud Project and configure an OAuth Client. Downlaod the corresnponding `client_id.json` and `client_secret.json` and place them in the `app/` directory.

### Development
- Run `docker-compose up`
- App will be exposed on localhost:8080

### Deployment
- Modify `docker-compose.prod.yml` according to your needs
- Run `docker-compose -f docker-compose.prod.yml up -d`
- Think about adding a reverse proxy or use something like Traefik

## Available endpoints
- `/notes`
- `/notes-api`
- `/random-note`
- `/update`

