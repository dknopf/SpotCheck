#!/bin/sh
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options  # for suppressing the browser head
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from google.cloud import datastore
import re
import time
from datetime import datetime
import json
import atexit
import pandas as pd
import multiprocessing as mp
import os
import sys
from pathlib import Path
from email.message import EmailMessage
import smtplib
"""
Creates a webdriver to run the scraping in
"""
options = webdriver.ChromeOptions()
options.add_argument('--no-proxy-server')
options.add_argument('headless')
options.add_argument('log-level=3') # Suppresses error messages

abspath = Path(os.path.abspath(''))
print('abspath is', abspath)
path = abspath / 'chromedriver'
print('path is', path)
path = path.as_posix()
print('path after change is', path)
options.binary_location = (abspath / 'chrome.exe').as_posix()
print('binary path is', options.binary_location)



#Global Variables
webdriver_list = []
class_dict = {}


print('above quit webscrapers')
def quit_webdrivers():
    for instance in webdriver_list:
        instance.quit()
    print('webdrivers quit')
    
atexit.register(quit_webdrivers)
print('below quit webscrapers')


def NavigateSearch():
    try:
        print('got into navigate search')
        global webdriver_list
        driver = webdriver.Chrome(executable_path=path, options=options)
        webdriver_list.append(driver)

        driver.get('https://owaprod-pub.wesleyan.edu/reg/!wesmaps_page.html?stuid=&facid=NONE&page=search&term=1209')
        driver.find_element(By.XPATH, '//input[@name="seatavail"]').click()
        driver.find_element(By.XPATH, '//input[@value="List Course(s)"]').click()
        print('page after navigate search is: ', driver.current_url)
        ScrapeFullCourseList(driver)
    except:
        quit_webdrivers()
        raise

def ScrapeFullCourseList(driver):
    try:
        print('got into scrape full course list')
        tbody = driver.find_element(By.XPATH, '//html/body/table/tbody/tr[3]/td/table/tbody')
        list_of_links = tbody.find_elements(By.TAG_NAME, 'a')
        print('num links: ', len(list_of_links))
        num_p = 4 #Num processess = num cpus
        #num_p = mp.cpu_count() #Num processess = num cpus
        list_of_links = list_of_links[:6]
        if __name__ == '__main__':
            with mp.Pool(num_p) as pool:
                results = [pool.apply_async(ScrapeIndividualPage, args = (link.get_attribute('href'),), callback = callback) for link in list_of_links]
                pool.close()
                pool.join()
    except:
        quit_webdrivers()
        raise

def callback(info_tuple):
    global class_dict
    class_dict[info_tuple[0]] = info_tuple[1]

def ScrapeIndividualPage(link):
    try:
        print('now scraping individual page at link: ', link)
        total_num_seats = 0
        class_name = 'DEFAULT TITLE'
        global webdriver_list

        individual_driver = webdriver.Chrome(executable_path=path, options=options)
        webdriver_list.append(individual_driver)
        individual_driver.get(link)

        class_name = individual_driver.find_element(By.XPATH, '//span[@class="title"]').text

        seats_avail_list = individual_driver.find_elements(By.XPATH, '//td[contains(text(), "Seats Available:")]')
        for entry in seats_avail_list:
            num_seats = int(re.search('(?<=Seats Available: )-?\d+', entry.text).group(0))
            if num_seats > 0:
                total_num_seats += num_seats
        return (class_name, total_num_seats)

    except:
        quit_webdrivers()
        raise


def ScrapeClasses(datastore_client):
    print('got into the top of ScrapeClasses')
    #if __name__ == '__main__':
    NavigateSearch()
    print('got past navigate searches')
    UpdateEntities(datastore_client)
    return class_dict
    #else:
    #    print('NOT ON MAIN IN SCRAPE CLASSES')
#if __name__ == '__main__':
#    print(ScrapeClasses())


def UpdateEntities(datastore_client):
    print('got into update entities')
    query = datastore_client.query(kind='course')
    for course in class_dict:
        query.key_filter(datastore_client.get(datastore_client.key('course', course)), '=')
        results = list(query.fetch())
        if len(results) > 1:
            print("GOT MORE THAN ONE RESULT IN QUERY")
        elif len(results) == 1:
            if results[0].seats_avail == 0 and class_dict[course] > 0:
                #SEND AN EMAIL
                results[0]['seats_avail'] = class_dict[course]
                datastore_client.put(results[0])
            elif results[0].seats_avail != class_dict[course]:
                results[0]['seats_avail'] = class_dict[course]
                datastore_client.put(results[0])
        elif len(results) == 0:
            new_entity = datastore.Entity(key=datastore_client.key('course', course))
            new_entity.update({
                'seats_avail' : class_dict[course],
                'emails' : []
                })
            datastore_client.put(new_entity)
#final_dict = {}

#alpha_driver.get('https://owaprod-pub.wesleyan.edu/reg/!wesmaps_page.html?stuid=&facid=NONE&crse_list=ENGL&term=1209&offered=Y#fall')
#table_block = alpha_driver.find_element(By.XPATH, '/html/body/table/tbody/tr[2]/td/table[1]/tbody')
#links = table_block.find_elements(By.XPATH, '//a[contains(text(), "ENGL"))]')
#for link in links:
#    title = individual_driver.find_element(By.XPATH, '//span[@class="title]').text
#    final_dict[title] = []
#    individual_driver.get(link.get_attribute('href'))
#    statuses = individual_driver.find_elements(By.XPATH, '//a[contains(text(), "Instruction")]')
#    for status in statuses:
#        final_dict[title].append(status.text)

#print(final_dict)