import os
from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
# account_sid = os.environ['AC756db440eb6b96fd8bd7cc4620b802fa']
# auth_token = os.environ['133bc1cecb2dd3a8c65b86deaf728275']
client = Client('AC756db440eb6b96fd8bd7cc4620b802fa', '133bc1cecb2dd3a8c65b86deaf728275')

message = client.messages \
                .create(
                     body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                     from_='+12029984424',
                     to='+18056890014'
                 )

print(message.sid)