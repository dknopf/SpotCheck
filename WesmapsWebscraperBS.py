import requests
from bs4 import BeautifulSoup
import re
import multiprocessing as mp
from google.cloud import datastore
import yagmail
from datetime import datetime
import config as cf
from twilio.rest import Client
from dotenv import load_dotenv
import os


# GLOBAL VARIABLES
class_dict = {}

url_prefix = 'https://owaprod-pub.wesleyan.edu/reg/'

messages_to_send_dict = {}

# Loads the twilio account credentials stored in a .env file
load_dotenv()


# print(src)
def ScrapeMainPage():
    print('\n \n got into scrape main page \n \n')
    result = requests.get(
        'https://owaprod-pub.wesleyan.edu/reg/!wesmaps_page.html')
    src = result.content
    soup = BeautifulSoup(src, 'lxml')
    other_header = soup.find('b', text='OTHER')
    links = other_header.find_all_previous('a', href=re.compile('subj_page'))
    # links = links[:6]
    print('above multiprocessing')
    #num_p = mp.cpu_count()
    #print('num processors: ', num_p)
    print('got into if name is main in multiprocessing')
    print('len links in main page is: ', len(links))
    for i, link in enumerate(links):
        print('now scraping link number: ', str(i),
              'out of total num links: ', len(links))
        ScrapeSubjectPage(url_prefix + link.attrs['href'])
    # with mp.Pool(num_p) as pool:
    #    results = [pool.apply_async(ScrapeSubjectPage, args = (url_prefix + link.attrs['href'],)) for link in links]
    #    pool.close()
    #    pool.join()
    # if __name__ == '__main__':
    #    print('got into if name is main in multiprocessing')
    #    with mp.Pool(num_p) as pool:
    #        results = [pool.apply_async(ScrapeSubjectPage, args = (url_prefix + link.attrs['href'],)) for link in links]
    #        pool.close()
    #        pool.join()
    print('below multiprocessing')


def ScrapeSubjectPage(link):
    print('\n got into scrape subject page at link: ', link, '\n')
    subject_content = requests.get(link).content
    subj_soup = BeautifulSoup(subject_content, 'lxml')
    """
    Another place with fall/spring specific content
    """
    courses_offered_link = subj_soup.find(href=re.compile(
        'offered=Y#' + cf.dateObj.semester))  # CHANGE THIS TO offered=Y#FALL IF NECESSARY
    # print(courses_offered_link.text)
    try:
        ScrapeCoursesOfferedPage(
            url_prefix + courses_offered_link.attrs['href'])
    except:
        pass


def ScrapeCoursesOfferedPage(link):
    offered_content = requests.get(link).content
    offered_soup = BeautifulSoup(offered_content, 'lxml')

    # fall courses are all before the "spring" header, spring classes all after
    spring = offered_soup.find('a', attrs={'name': 'spring'})

    if cf.dateObj.semester == 'fall':
        links = spring.find_all_previous(href=re.compile('crse'))
    elif cf.dateObj.semester == 'spring':
        links = spring.find_all_next(href=re.compile('crse'))
    #links = offered_soup.find_all(href=re.compile('crse'))
    global linksScraped
    for link in links:
        link_href = link.attrs['href']
        # if not WasScrapedAlready(link):
        if link_href not in linksScraped:
            linksScraped[link_href] = 'Scraped'
            print('Link not in dict in scrape courses offered is: ', link_href)
            print(' linksScraped dict is: ', linksScraped)
            ScrapeIndividualPage(url_prefix + link_href)


def ScrapeIndividualPage(link):
    content = requests.get(link).content
    soup = BeautifulSoup(content, 'lxml')
    course_name = soup.find('span', class_='title').text
    depts = soup.find_all('a', text=re.compile('^[A-Z&]{3,4}$'))
    print('depts for: ', course_name, ' are: ', depts)
    seat_entries = soup.find_all('td', text=re.compile('Seats Available: '))
    total_num_seats = 0
    for entry in seat_entries:
        seats_avail = int(
            re.search('(?<=Seats Available: )-?\d+', entry.text).group(0))
        if seats_avail > 0:
            total_num_seats += seats_avail
    UpdateEntries(course_name, total_num_seats, depts, link)
    #print(course_name, total_num_seats)


def UpdateEntries(course, num_seats, depts, link):
    masterEntity = RetrieveMasterEntity(client)
    # UPDATE THE MASTER ENTITY LIST TO HAVE DEPTS
    # RERUN EVERY FEW MONTHS AT MOST
    # for dept in depts:
    #    if dept.text not in masterEntity[cf.dateObj.courseList]:
    #        masterEntity[cf.dateObj.courseList].append(dept.text)
    #        client.put(masterEntity)
    # MAKE THIS A DICT FOR EASY LOOKUP
    if course not in masterEntity[cf.dateObj.courseList]:
        masterEntity[cf.dateObj.courseList].append(course)
        client.put(masterEntity)

    print('made it into update entries for course: ', course)
    query = client.query(kind='course')
    print('made it past query')
    query.key_filter((client.key('course', course)), '=')
    print('made it past query key filter')
    results = list(query.fetch())
    print('made it past fetching query. Len query is: ', len(results))
    if len(results) > 1:
        print("GOT MORE THAN ONE RESULT IN QUERY")
    elif len(results) == 1:
        print('got into len results = 1. Found a matching course')
        # RUN EVERY FEW MONTHS AT MOST
        #"""UPDATE DEPTS"""
        # for i, dept in enumerate(depts):
        #        print('dept.text for course: ', course, ' is: ', dept.text)
        #        results[0]['dept' + str(i)] = dept.text

        if results[0]['seats_avail'] == 0 and num_seats > 0:
            AddAggregatedMessages(results[0]['emails'], course, link)
            results[0]['seats_avail'] = num_seats
        elif results[0]['seats_avail'] != num_seats:
            results[0]['seats_avail'] = num_seats

        results[0]['link'] = link
        results[0]['date_scraped'] = datetime.utcnow()
        client.put(results[0])
    # A course not in course list has been found
    elif len(results) == 0:
        print('got into len results is 0')
        new_entity = datastore.Entity(key=client.key('course', course))
        new_entity.update({
            'seats_avail': num_seats,
            'emails': []
        })
        for i, dept in enumerate(depts):
            new_entity['dept' + str(i)] = dept.text
        new_entity['link'] = link
        new_entity['date_scraped'] = datetime.utcnow()

        client.put(new_entity)
        print('put new entity in: ', new_entity.key.name)


def AddAggregatedMessages(user_list, course, link):
    """
    Creating a list of strings and then using ''.join(str_list)
    is much faster than concatenating many strings together
    """
    global messages_to_send_dict

    for user in user_list:
        if re.search("\d{9,10}", user):  # Text
            segment = '-' + course + '\n'
        elif re.search("@", user):
            segment = '-<a href ="' + link + '">' + course + '</a>\n'
        try:
            if messages_to_send_dict[user] != []:
                messages_to_send_dict[user].append(segment)
        except:
            messages_to_send_dict[user] = [
                'Congrats, a spot has opened up in: \n' + segment]


def SendMessages():
    global messages_to_send_dict
    masterEntity = RetrieveMasterEntity(client)

    # oauth2 file is uploaded to gcloud not github
    yag = yagmail.SMTP('spotcheckwes@gmail.com',
                       oauth2_file="oauth2_creds.json")
    twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"),
                           os.getenv("TWILIO_ACCOUNT_SECRET"))

    for user in messages_to_send_dict:
        if re.search("\d{9,10}", user):  # Text
            messages_to_send_dict[user].append(
                '\nAct fast, others were notified too! \nVisit https://www.spotcheck.space/login to see your subscribed courses/unsubscribe')
            contents = ''.join(messages_to_send_dict[user])
            message = twilio_client.messages \
                .create(
                    body=contents,
                    messaging_service_sid='MGce3b91ee5ecc126b6e230f1afb8c2c5b',
                    to="+1" + user
                )
            masterEntity[cf.dateObj.textsSent] += 1
            masterEntity[cf.totalTextsSent] += 1
        elif re.search("@", user):  # Email
            messages_to_send_dict[user].append(
                '\nMake sure to act fast, other people have been notified and are trying to get this seat too! \nClick <a href="https://www.spotcheck.space/login">here</a> to see your subscribed courses/unsubscribe</p>')
            contents = '<p>' + ''.join(messages_to_send_dict[user])
            yag.send(user, 'A Spot is Open in a Class You Want!', contents)
            masterEntity[cf.dateObj.emailsSent] += 1
            masterEntity[cf.totalEmailsSent] += 1
    messages_to_send_dict = {}
    client.put(masterEntity)


def WasScrapedAlready(link):
    now = datetime.utcnow()
    if now.minute < 10:
        if now.hour == 0:
            prev_time = now.replace(
                day=now.day-1, hour=23, minute=now.minute+50)
        else:
            prev_time = now.replace(hour=now.hour-1, minute=now.minute+50)
    else:
        prev_time = now.replace(minute=now.minute-10)
    query = client.query(kind='course')
    query.add_filter('date_scraped', '<', prev_time)
    results = list(query.fetch())
    if len(results) == 0:
        return False
    else:
        return True


def RetrieveMasterEntity(client):
    """
    Only works if the current masterEntity is the first one
    """
    query = client.query(kind='masterEntity')
    print('made it past query')
    results = list(query.fetch())
    return results[0]


def CreateMasterEntity(client):
    masterEntity = datastore.Entity(key=client.key('masterEntity'))
    masterEntity.update({
        cf.dateObj.courseList: []
    })
    client.put(masterEntity)


def StartFunction(datastore_client):
    global client
    client = datastore_client
    global linksScraped
    cf.dateObj.GetCurrDate()  # Update date
    linksScraped = {'Test': 'Scraped'}
    print('GOT INTO START FUNCTION AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH')
    ScrapeMainPage()
    SendMessages()
