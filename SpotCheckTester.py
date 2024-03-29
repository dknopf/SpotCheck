from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# for suppressing the browser head
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import multiprocessing as mp
from pathlib import Path
import os
import atexit
import time

"""
Creates a webdriver to run the scraping in
"""
options = webdriver.ChromeOptions()
options.add_argument('--no-proxy-server')
options.add_argument('headless')
options.add_argument('log-level=3')  # Suppresses error messages

abspath = Path(os.path.abspath(''))
print('abspath is', abspath)
# This only works on a windows computer, dummy
path = abspath / 'chromedriver.exe'
print('path is', path)
path = path.as_posix()
print('path after change is', path)
# Wow who let you write an absolute path like this, idiot
path = r'C:\Users/daniel/Documents/Code/Assorted/chromedriver.exe'
options.binary_location = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
print('binary path is', options.binary_location)

webdriver_list = []


def quit_webdrivers():
    for instance in webdriver_list:
        instance.quit()
    print('webdrivers quit')


def callback(ignore):
    print('scraped')


def scrape():
    print('got into scrape')
    num_p = mp.cpu_count()
    list_of_depts = ['ENGL, COMP', 'QAC, AFAM', 'FGSS, EDST',
                     'RELI, ENVS', 'GOVT, SOC', 'AMST, CSPL', 'PHIL, ANTH', 'CCIV, CEAS']
    if __name__ == '__main__':
        with mp.Pool(num_p) as pool:
            results = [pool.apply_async(ScrapeIndividualPage, args=(
                department,), callback=callback) for department in list_of_depts]
            pool.close()
            pool.join()


def ScrapeIndividualPage(department):
    global webdriver_list
    driver = webdriver.Chrome(executable_path=path, options=options)
    webdriver_list.append(driver)

    try:
        Subscribe(driver, department)
        Unsubscribe(driver, department)
        driver.quit()
    except:
        print('got into except')
        quit_webdrivers()
        raise


def Subscribe(driver, department):
    driver.get('https://www.spotcheck.space/')
    print('passed driver.get')
    emailInput = driver.find_element(By.XPATH, '//input[@id="email"]')
    emailInput.send_keys("SELENIUM_TEST_" + department[0] + "1")
    courseInput = driver.find_element(By.XPATH, '//input[@id="autocomplete"]')
    courseInput.send_keys(department)
    subscribeButton = driver.find_element(
        By.XPATH, '//input[@id="subscribeButton"]')
    subscribeButton.click()


def Unsubscribe(driver, department):
    print('got into unsubscribe')

    driver.get("https://www.spotcheck.space/login?")
    emailInput = driver.find_element(By.XPATH, '//input[@id="email"]')
    print('found email input')
    emailInput.send_keys("SELENIUM_TEST_" + department[0] + "1")
    print('sent keys')
    emailInput.submit()
    print('submitted')

    unsubscribeLinks = driver.find_elements(
        By.XPATH, '//input[@class="unsubscribeButton"]')
    print('len unsubscribe links for: ', "SELENIUM_TEST_" +
          department[0] + "1", len(unsubscribeLinks))
    for link in unsubscribeLinks:
        print('link is: ', link.get_attribute("id"))
        link.click()
    print('finished unsubscribe')


if __name__ == '__main__':

    scrape()
