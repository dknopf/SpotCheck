# SpotCheck
The www.SpotCheck.space webapp alerts you if space in a class you want opens up during Wesleyan schedule adjustment. Simply put your email or phone number and the classes you're interested in on the subscribe page and click enter and you will receive an email or text when a spot opens up!

# Setup

1. Log into the Google Cloud SDK
2. Make sure that your current project is set to wescraper (old name of SpotCheck)
3. Install twilio and yagmail credentials
   * Twilio credentials require you to create a .env file and put the `TWILIO_ACCOUNT_SID='<sid here>'` and `TWILIO_ACCOUNT_SECRET='<secret here>'`
   * Gmail + Google API credentials require you to create an oauth2_creds.json file. See instructions here: https://developers.google.com/identity/protocols/oauth2
   * NEVER EVER UPLOAD THESE FILES TO GITHUB, ONLY TO GOOGLE CLOUD. PUT THEM IN YOUR GITIGNORE. IM SERIOUS, I ACCIDENTALLY UPLOADED MY GCLOUD CREDENTIALS TO GITHUB ONCE AND SOMEONE USED MY ACCOUNT TO MINE CRYPTOCURRENCY. ITS NOT THE VIBE, DON'T DO IT.
4. Create and activate a python virtual env: https://docs.python.org/3/library/venv.html
5. Install python packages with `pip install -r requirements.txt`


# Deployment

## App:

`gcloud app deploy`

## Cron:

`gcloud app deploy cron.yaml`

# Changing semesters

1. Create an array field in masterEntity in datastore that is `courseList<Semester><year>`
2. Delete all user and course entities from datastore. Really there should be a script that handles this but there isn't yet
3. I think all the other semester switching stuff should be handled automatically now

## After Adjustment Ends

1. Comment out the cron information in `cron.yaml` below line 1, leaving line 1: `cron:` intact, then upload that cron job to google cloud.
2. You may want to disable the app altogether after the two week adjustment period, because sometimes Google Cloud just charges a ton of money


# How SpotCheck Works

The crux of SpotCheck is that it is a Python Flask app that uses BeautifulSoup to scrape the WesMaps website every 5 minutes. All of the scraping and email/text sending functionality is handled in `WesmapsWebscraperBS.py`. In the `UpdateEntries` function, the scraper will check if the current course exists in datastore, and if it does then it updates the seats_avail, adding a scheduled message to all the users subscribed to the course if seats are available. After the scraper has run and checked all courses it will send all messages to users who need to be updated.

## Technologies Used:

* SpotCheck is a Python Flask app, using BeautifulSoup for webscraping.
* SpotCheck is hosted on Google App Engine and uses the Google Datastore database. This is super outdated tech, so if someone wants to update this project to use Firebase and Firestore that would be splendid
* The domain is from domain.com. Right now it is set to auto-renew the domain on JULY 3 2021.
* I am using a Google Cloud Load Balancer so that SSL is enforced and spotcheck can use https. This is nice because Google doesn't warn everyone who comes to the site that their info might be stolen, but also the load balancer somehow costs like a dollar a day which is nuts.
* Yagmail is being used to send emails from spotcheckwes [at] gmail [dot] commmmmm
* Twilio is being used to send text messages, but ONLY TO PEOPLE WITH US AREA CODES. It will automatically add on the +1 at the front, and maybe get rid of any other area code that is entered in.
