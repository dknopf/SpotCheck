import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()


# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
# account_sid = os.environ['AC756db440eb6b96fd8bd7cc4620b802fa']
# auth_token = os.environ['133bc1cecb2dd3a8c65b86deaf728275']
client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_ACCOUNT_SECRET"))


for number in ['+19173992277', '+12036770940']:
    message = client.messages \
                    .create(
                        body="*in dracula voice* Good eeeveeenning \nhttps://spotcheck.space",
                        messaging_service_sid='MGce3b91ee5ecc126b6e230f1afb8c2c5b',
                        to=number
                    )

print(message.sid)