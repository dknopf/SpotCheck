import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

# This file is a template for how to send sms files, it itself is almost never used

# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure


def sendMessage(number, messageText):
    twilioClient = Client(os.getenv("TWILIO_ACCOUNT_SID"),
                          os.getenv("TWILIO_ACCOUNT_SECRET"))
    message = twilioClient.messages \
        .create(
            body=messageText,
            messaging_service_sid='MGce3b91ee5ecc126b6e230f1afb8c2c5b',
            to="+1" + number
        )
