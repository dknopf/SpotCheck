# SpotCheck
The www.SpotCheck.space webapp alerts you if space in a class you want opens up during Wesleyan schedule adjustment. Simply put your email or phone number and the classes you're interested in on the subscribe page and click enter and you will receive an email or text when a spot opens up!


# RIP SPOTCHECK :( 
As of October 31st, 2022, SpotCheck will no longer be supported. Continuing to run it would require me to deal with updating package versions and other such nonsense, and since I have graduated I am letting this website die so that some new plucky young underclassmen can build their own version and get that valuable experience. SpotCheck had a good few years, it served almost 2,000 users and sent over 8,000 texts and emails, and helped dozens of students get into classes they wanted. This was my first project, my baby, and I will miss it dearly.

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

Make sure to delete all old versions on GAE each time you redeploy, otherwise you will be charged a BUNCH.

## Cron:

`gcloud app deploy cron.yaml`

# Changing semesters

All of this functionality should be automatically handled by the update_semester path. There is a cron job that runs on the 1st of November, August, and April to call this, but **it is not enabled right now, so it needs to be reenabled and manually run via the cloud scheduler**. Here is what needs to be done each semester in case the function isn't working properly, or if you want to manually update SpotCheck.

1. Create new fields for new data
  * numUsers
  * emailsSent
  * textsSent
  * courseList
  * userList
2. Send out a message to all users from last semester telling them that SpotCheck is available again. This doesn't happen during the summert refresh, since only freshmen have adjustment during the summer so upperclassmen shouldn't be notified. Right now this functionality is disabled as well, so it will not send out the welcome message.
3. Double check that all user and course entities have been deleted from datastore.

## After Adjustment Ends

1. Comment out the cron job for /schedule in `cron.yaml` below line 1, leaving line 1: `cron:` intact, then upload that cron job to google cloud.
2. Don't disable the app during this period, as it will shut off spotcheck.space, and showing a blank page to potential viewers/portfolio lookers is bad.


# How SpotCheck Works

The crux of SpotCheck is that it is a Python Flask app that uses BeautifulSoup to scrape the WesMaps website. It takes about 5 minutes for the code to run, and then there is a scheduled 1 minute interval to ensure that duplicate runs don't happen simulatenously (which is the every 1 minute in the cron job). All of the scraping and email/text sending functionality is handled in `WesmapsWebscraperBS.py`. In the `UpdateEntries` function, the scraper will check if the current course exists in datastore, and if it does then it updates the seats_avail, adding a scheduled message to all the users subscribed to the course if seats are available. After the scraper has run and checked all courses it will send all messages to users who need to be updated.

## Technologies Used:

* SpotCheck is a Python Flask app, using BeautifulSoup for webscraping.
* SpotCheck is hosted on Google App Engine and uses the Google Datastore database. This is super outdated tech, so if someone wants to update this project to use Firebase and Firestore that would be splendid
* The domain is from domain.com. Right now it is set to auto-renew the domain in JULY 2022.
* I am using a Google Cloud Load Balancer so that SSL is enforced and SpotCheck can use https. This is nice because Google doesn't warn everyone who comes to the site that their info might be stolen, but also the load balancer is a bit expensive.
* Yagmail is being used to send emails from spotcheckwes [at] gmail [dot] com
* Twilio is being used to send text messages, but ONLY TO PEOPLE WITH US AREA CODES. SpotCheck will automatically add on the +1 at the front, and get rid of any other area code that is entered in.
