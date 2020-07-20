import requests
from bs4 import BeautifulSoup
import re
import multiprocessing as mp
from google.cloud import datastore
import yagmail




#GLOBAL VARIABLES
class_dict = {}

url_prefix = 'https://owaprod-pub.wesleyan.edu/reg/'

#print(src)
def ScrapeMainPage():
    print('\n \n got into scrape main page \n \n')
    result = requests.get('https://owaprod-pub.wesleyan.edu/reg/!wesmaps_page.html')
    src = result.content
    soup = BeautifulSoup(src, 'lxml')
    links = soup.find_all('a', href=re.compile('subj_page'))
    links = links[:6]
    print('above multiprocessing')
    #num_p = mp.cpu_count()
    #print('num processors: ', num_p)
    print('got into if name is main in multiprocessing')
    for link in links:
        ScrapeSubjectPage(url_prefix + link.attrs['href'])
    #with mp.Pool(num_p) as pool:
    #    results = [pool.apply_async(ScrapeSubjectPage, args = (url_prefix + link.attrs['href'],)) for link in links]
    #    pool.close()
    #    pool.join()
    #if __name__ == '__main__':
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
    courses_offered_link = subj_soup.find(href=re.compile('offered=Y#fall')) #CHANGE THIS TO offered=Y#FALL IF NECESSARY
    #print(courses_offered_link.text)
    ScrapeCoursesOfferedPage(url_prefix + courses_offered_link.attrs['href'])

def ScrapeCoursesOfferedPage(link):
    offered_content = requests.get(link).content
    offered_soup = BeautifulSoup(offered_content, 'lxml')
    links = offered_soup.find_all(href=re.compile('crse'))
    for link in links:
        ScrapeIndividualPage(url_prefix + link.attrs['href'])

def ScrapeIndividualPage(link):
    content = requests.get(link).content
    soup = BeautifulSoup(content, 'lxml')
    course_name = soup.find('span', class_='title').text
    seat_entries = soup.find_all('td', text = re.compile('Seats Available: '))
    total_num_seats = 0
    for entry in seat_entries:
        seats_avail = int(re.search('(?<=Seats Available: )-?\d+', entry.text).group(0))
        if seats_avail > 0:
                total_num_seats += seats_avail
    UpdateEntries(course_name, total_num_seats)
    #print(course_name, total_num_seats)

def UpdateEntries(course, num_seats):
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
        print('got into len results =1 ')
        if results[0]['seats_avail'] == 0 and num_seats > 0:
            yag=yagmail.SMTP('spotcheckwes@gmail.com','SpotCheckWes1234!')
            contents = ["Congrats, a spot has opened up in: " + course + 'Click here to see your subscribed courses/unsubscribe: www.spotcheck.space']

            for email in results[0]['emails']:
                yag.send(email, 'A spot has opened up in ' + course, contents)



            results[0]['seats_avail'] = num_seats
            client.put(results[0])
        elif results[0]['seats_avail']  != num_seats:
            results[0]['seats_avail'] = num_seats
            client.put(results[0])
    elif len(results) == 0:
        print('got into len results is 0')
        new_entity = datastore.Entity(key=client.key('course', course))
        new_entity.update({
            'seats_avail' : num_seats,
            'emails' : []
            })
        client.put(new_entity)
        print('put new entity in: ', new_entity.key.name)


def StartFunction(datastore_client):
    global client
    client = datastore_client
    ScrapeMainPage()

#if __name__ == '__main__':
#    print('GOT INTO IF NAME IS MAIN \n \n \n AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH')
#    ScrapeMainPage()
#ScrapeSubjectPage('https://owaprod-pub.wesleyan.edu/reg/!wesmaps_page.html?stuid=&facid=NONE&subj_page=CCIV&term=1209')
