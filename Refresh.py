from google.cloud import datastore

from send_sms import sendMessage
import yagmail
import re
import config as cf


def Refresh(datastore_client):
    global client
    client = datastore_client
    updateMasterEntity()
    if cf.dateObj.month > 5 and cf.dateObj.month < 9:
        # It is summer, don't send the message to users but make sure they don't get notified when a seat opens during freshman adjustment
        print("It is summer")
    else:
        # It is not summer.
        UpdateUsers()
    ClearCourses()


"""
Updates the master entity to add new fields for the new semester, such as emailsSentFall2021
"""


def updateMasterEntity():
    query = client.query(kind='masterEntity')
    ME = list(query.fetch())[0]
    # Check if field exists already to avoid overwriting

    fieldsDict = {"listFields":
                  {
                      "fields": [cf.dateObj.courseList, cf.dateObj.userList],
                      "default": []
                  },
                  "intFields":
                  {
                      "fields": [cf.dateObj.emailsSent,
                                 cf.dateObj.textsSent,
                                 cf.dateObj.numUsers],
                      "default": 0
                  }
                  }
    for fieldType in ["listFields", "intFields"]:
        for field in fieldsDict[fieldType]["fields"]:
            try:
                # WIll error out if field doesn't exist, but if it does exist will do nothing
                if ME[field] == "test":
                    pass
            except:
                ME[field] = fieldsDict[fieldType]["default"]
    client.put(ME)


def SendMessage(username):
    yag = yagmail.SMTP('spotcheckwes@gmail.com',
                       oauth2_file="oauth2_creds.json")

    # The text welcome back message has to be shorter since Twilio counts every 160 characters as a text message so sending a long text is pricey
    welcomeBackMessageEmail = "Hello SpotCheck Users! This month is the start of a new pre-reg period, and SpotCheck is once again open for business! To be alerted when a seat opens in a class you want during adjustment, simply go to https://spotcheck.space and sign up. The earlier you sign up, the quicker you'll be notified when a seat opens! All account information has been deleted at the end of last semester so you will have to sign up again. If you have any SpotCheck success stories, please tell me about them at spotcheckwes@gmail.com! \n\nAnd to all my fellow seniors doing their final pre-reg, it’s been a pleasure knowing you all. Let’s make this last semester the best one yet. \n\nLove, \nSpotCheck"
    welcomeBackMessageText = "This month is the start of a new pre-reg period, and SpotCheck is open for business! To be alerted when a seat opens in a class you want during adjustment, go to https://spotcheck.space and sign up. All account information has been deleted at the end of last semester so you will have to sign up again. \n\nAnd to all my fellow seniors doing their final pre-reg, it’s been a pleasure knowing you all. Let’s make this last semester the best one yet \n\nLove, \nSpotCheck"

    if re.search("\d{9,10}", username):  # Text
        sendMessage(username, welcomeBackMessageText)
    elif re.search("@", username):  # Email
        yag.send(username, 'SpotCheck Is Now Active Again!',
                 welcomeBackMessageEmail)


"""
Sends all of the current users a message saying that SpotCheck is starting again and then deletes the user entity
"""


def UpdateUsers():

    query = client.query(kind='user')
    results = list(query.fetch())
    for result in results:
        key = result.key
        username = result["username"]
        # SendMessage(username)
        client.delete(key)


def ClearCourses():
    query = client.query(kind='course')
    print('made it past query for all courses in clearcourses')
    results = list(query.fetch())
    for result in results:
        key = result.key
        client.delete(key)
