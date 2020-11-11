import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()


# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_ACCOUNT_SECRET"))


for number in ['+19173992277', '+12036770940']:
    message = client.messages \
                    .create(
                        body="*in dracula voice* Good eeeveeenning \nhttps://spotcheck.space",
                        messaging_service_sid='MGce3b91ee5ecc126b6e230f1afb8c2c5b',
                        to=number
                    )

print(message.sid)